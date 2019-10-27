import asyncio
import pytest

from flatbot.config import Config
from flatbot.db import Storage
from flatbot.bot import notifications, scheduler, scraper


results_list = [
    [
        ("M1", "200"),
        ("M2", "300")
    ],
    []
]

@pytest.mark.parametrize('results', results_list)
async def test_run_ok(results, config_path, monkeypatch):
    class MockScraper:
        def __init__(self, results):
            self.results = results

        async def run(self, _):
            return self.results

    class MockHandler:
        def on_error(self, channel_id, url):
            pass

    base_results = [scraper.ScrapeResult(n, p) for n, p in results]
    mock_scraper = MockScraper(base_results)

    async def dummy_notify(_, results):
        assert results == base_results

    notifier = notifications.Notifier()
    monkeypatch.setattr(notifier, 'notify', dummy_notify)
    storage = Storage()
    config = Config(config_path)
    channel = scheduler.URLChannel("", mock_scraper, storage, notifier, MockHandler(), config)

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
    channel = scheduler.URLChannel("", mock_scraper, storage, notifier, MockHandler(), config)

    channel.run()
    await asyncio.sleep(1)
    await channel.cancel()
