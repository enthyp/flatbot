import asyncio
import pytest

from flatbot.config import Config
from flatbot.db import Storage
from flatbot.bot import notifications, scheduler, scraper


results_list = [
    {
        ("M1", "200"),
        ("M2", "300")
    },
    set()
]

@pytest.mark.parametrize('results', results_list)
async def test_run_ok(results, config_path, monkeypatch):
    class MockScraper:
        def __init__(self, results):
            self.results = results

        async def run(self):
            return self.results

    class MockHandler:
        def on_error(self, id):
            pass

    base_results = set([scraper.ScrapeResult(n, p) for n, p in results])
    id = 1
    mock_scraper = MockScraper(base_results)

    async def dummy_notify(channel_id, results):
        assert channel_id == id
        assert results == base_results

    notifier = notifications.Notifier()
    monkeypatch.setattr(notifier, 'notify', dummy_notify)
    storage = Storage()
    config = Config(config_path)
    channel = scheduler.URLChannel(id, mock_scraper, storage, notifier, MockHandler(), config)

    channel.run()
    await asyncio.sleep(1)
    await channel.cancel()


async def test_run_fail(config_path):
    channel_id = 1
    class MockScraper:
        def __init__(self, id):
            self.id = id

        async def run(self):
            raise Exception

    class MockHandler:
        async def on_error(self, id):
            pass

    mock_scraper = MockScraper(channel_id)
    notifier = notifications.Notifier()
    storage = Storage()
    config = Config(config_path)
    channel = scheduler.URLChannel(channel_id, mock_scraper, storage, notifier, MockHandler(), config)

    channel.run()
    await asyncio.sleep(1)
    await channel.cancel()
