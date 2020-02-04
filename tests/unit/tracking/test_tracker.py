import asyncio
import pytest

from flatbot.config import Config
from flatbot.db.storage import Storage
from flatbot.tracking.scrapers import BaseScraper
from flatbot import notifications


@pytest.fixture
def mock_storage(mocker):
    storage = mocker.Mock(spec=Storage)
    return storage


@pytest.fixture
def mock_scraper(mocker):
    scraper = mocker.Mock(spec=BaseScraper)
    return scraper


def test_add_remove(mock_storage, mock_scraper):
    pass


async def test_run(mock_storage, mock_scraper):
    pass


# TODO: all below goes to waste!

@pytest.mark.parametrize('results', results_list)
async def test_run_ok(results, config_path, mocker):
    class MockScraper:
        def __init__(self, results):
            self.results = results

        async def run(self, _):
            return self.results

    class MockHandler:
        def on_error(self, channel_id, url):
            pass

    base_results = [scrapers.ScrapeResult(n, p) for n, p in results]
    mock_scraper = MockScraper(base_results)

    async def dummy_notify(_, results):
        assert results == base_results

    notifier = notifications.Notifier()
    monkeypatch.setattr(notifier, 'notify', dummy_notify)
    storage = Storage()
    config = Config(config_path)
    channel = manager.URLChannel("", mock_scraper, storage, notifier, MockHandler(), config)

    channel.run()
    await asyncio.sleep(1)
    await channel.cancel()


async def test_run_fail(config_path):
    class MockScraper:
        async def run(self, url):
            raise Exception

    class MockHandler:
        async def on_error(self, channel_id, url):
            pass

    config = Config(config_path)
    mock_scraper = MockScraper()
    notifier = notifications.Notifier()
    storage = Storage()
    channel = manager.URLChannel("", mock_scraper, storage, notifier, MockHandler(), config)

    channel.run()
    await asyncio.sleep(1)
    await channel.cancel()
