import asyncio
import pytest
from itertools import chain, repeat

from flatbot.db.storage import Storage
from flatbot.tracking.manager import Manager
from flatbot.tracking.scrapers import BaseScraper
from flatbot.tracking.tracker import Tracker, TrackerFactory


@pytest.fixture
def mock_storage(mocker):
    storage = mocker.Mock(spec=Storage)
    return storage


@pytest.fixture
def mock_scraper(mocker):
    scraper = mocker.Mock(spec=BaseScraper)
    return scraper


@pytest.fixture
def mock_manager(mocker):
    manager = mocker.Mock(spec=Manager)
    return manager


# Helper for mocking coroutines.
async def async_return(value):
    return value


async def test_add_remove(config, mock_storage, mock_scraper):
    config = config('config_full.yml')
    mock_storage.add_track.return_value = async_return(None)
    mock_storage.remove_track.return_value = async_return(None)

    tracker = Tracker('url', mock_scraper, mock_storage, config)

    await tracker.add('kuba')
    mock_storage.add_track.assert_called_once_with('url', 'kuba')

    await tracker.remove('kuba')
    mock_storage.remove_track.assert_called_once_with('url', 'kuba')


async def test_tracker_factory(config, mocker, mock_storage, mock_scraper):
    with mocker.patch('flatbot.tracking.tracker.get_scraper') as mock_get_scraper:
        mock_get_scraper.return_value = mock_scraper
        config = config('config_full.yml')
        mock_storage.create_site.return_value = async_return(None)
        mock_storage.get_urls.return_value = async_return([])

        factory = TrackerFactory(mock_storage, config)
        await factory.get('url')
        mock_storage.create_site.assert_called_once_with('url')

        await factory.get_all()
        mock_storage.get_urls.assert_called_once()


@pytest.mark.slow
async def test_add_remove_db(config, storage, mocker):
    with mocker.patch('flatbot.tracking.tracker.get_scraper') as mock_get_scraper:
        mock_get_scraper.return_value = mock_scraper
        config = config('config_full.yml')
        storage = await storage(config)

        mock_storage = mocker.Mock()
        mock_storage.create_site.side_effect = storage.create_site
        mock_storage.add_track.side_effect = storage.add_track
        mock_storage.remove_track.side_effect = storage.remove_track

        factory = TrackerFactory(mock_storage, config)
        tracker = await factory.get('url')

        await tracker.add('kuba')
        mock_storage.add_track.assert_called_once_with('url', 'kuba')

        assert await storage.is_tracked('url')

        await tracker.remove('kuba')
        mock_storage.remove_track.assert_called_once_with('url', 'kuba')


async def test_check_updates(config, site, mock_storage, mock_scraper):
    config = config('config_full.yml')
    mock_storage.get_site.side_effect = [async_return(None), async_return(site)]
    mock_storage.update_site.return_value = async_return(None)
    mock_scraper.run.side_effect = [async_return(site), async_return(site)]

    tracker = Tracker('url', mock_scraper, mock_storage, config)
    assert await tracker.check_updates() == site
    assert not await tracker.check_updates()


@pytest.mark.slow
async def test_run(config, site, mocker, mock_storage, mock_scraper):
    #with mocker.patch('flatbot.tracking.tracker.Tracker.check_updates') as mock_check_updates:
        # mock_check_updates.side_effect = chain(
        #     [async_return(site)],
        #     map(lambda x: async_return(x), repeat(None))
        # )
    mock_storage.get_site.side_effect = chain(
        [async_return(None)],
        map(lambda x: async_return(x), repeat(site))
    )
    mock_storage.update_site.side_effect = chain(
        map(lambda x: async_return(x), repeat(None))
    )
    mock_scraper.run.side_effect = map(lambda x: async_return(x), repeat(site))
    config = config('config_full.yml')
    tracker = Tracker('url', mock_scraper, mock_storage, config)

    handler = mocker.Mock()
    handler.handle.return_value = async_return(None)
    tracker.update_handler = handler

    tracker.run()
    await asyncio.sleep(2)
    await tracker.cancel()

    mock_scraper.run.assert_called_with('url')
    handler.handle.assert_called_with(tracker.id, site)

# @pytest.mark.parametrize('results', results_list)
# async def test_run_ok(results, config_path, mocker):
#     class MockScraper:
#         def __init__(self, results):
#             self.results = results
#
#         async def run(self, _):
#             return self.results
#
#     class MockHandler:
#         def on_error(self, channel_id, url):
#             pass
#
#     base_results = [scrapers.ScrapeResult(n, p) for n, p in results]
#     mock_scraper = MockScraper(base_results)
#
#     async def dummy_notify(_, results):
#         assert results == base_results
#
#     notifier = notifications.Notifier()
#     monkeypatch.setattr(notifier, 'notify', dummy_notify)
#     storage = Storage()
#     config = Config(config_path)
#     channel = manager.URLChannel("", mock_scraper, storage, notifier, MockHandler(), config)
#
#     channel.run()
#     await asyncio.sleep(1)
#     await channel.cancel()
#
#
# async def test_run_fail(config_path):
#     class MockScraper:
#         async def run(self, url):
#             raise Exception
#
#     class MockHandler:
#         async def on_error(self, channel_id, url):
#             pass
#
#     config = Config(config_path)
#     mock_scraper = MockScraper()
#     notifier = notifications.Notifier()
#     storage = Storage()
#     channel = manager.URLChannel("", mock_scraper, storage, notifier, MockHandler(), config)
#
#     channel.run()
#     await asyncio.sleep(1)
#     await channel.cancel()
