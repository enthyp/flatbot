import asyncio
import pytest
from itertools import chain, repeat

from flatbot.tracking.tracker import Tracker, TrackerFactory


async def test_add_remove(config, mock_storage, mock_scraper, async_return):
    config = config('config_full.yml')
    mock_storage.add_track.return_value = async_return(None)
    mock_storage.remove_track.return_value = async_return(None)

    tracker = Tracker('url', mock_scraper, mock_storage, config)

    await tracker.add('kuba')
    mock_storage.add_track.assert_called_once_with('url', 'kuba')

    await tracker.remove('kuba')
    mock_storage.remove_track.assert_called_once_with('url', 'kuba')


async def test_tracker_factory(config, async_return, mocker, mock_storage, mock_scraper):
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


# TODO: well, it's already an integration test!!!
@pytest.mark.slow
async def test_add_remove_db(config, mock_scraper, storage, mocker):
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


async def test_check_updates(config, site, async_return, mock_storage, mock_scraper):
    config = config('config_full.yml')
    mock_storage.get_site.side_effect = [async_return(None), async_return(site)]
    mock_storage.update_site.return_value = async_return(None)
    mock_scraper.run.side_effect = [async_return(site), async_return(site)]

    tracker = Tracker('url', mock_scraper, mock_storage, config)
    assert await tracker.check_updates() == site
    assert not await tracker.check_updates()


@pytest.mark.slow
async def test_run(config, site, async_return, mocker, mock_storage, mock_scraper):
    config = config('config_full.yml')
    tracker = Tracker('url', mock_scraper, mock_storage, config)

    # Mock updates.
    updates = chain(
        [async_return(site)],
        map(lambda x: async_return(x), repeat(None))
    )

    mock_check = mocker.patch.object(tracker, 'check_updates')
    mock_check.side_effect = updates

    handler = mocker.Mock()
    handler.handle.return_value = async_return(None)
    tracker.update_handler = handler

    tracker.run()
    await asyncio.sleep(2)
    await tracker.cancel()

    handler.handle.assert_called_with(tracker.id, site)
    mock_check.assert_called_with()
