from flatbot.db import Storage
from flatbot.tracking.scrapers import ScrapeResult


def test_storage_ok():
    channel_id = 1
    results = [
        ScrapeResult('res1', '22'),
        ScrapeResult('res2', '33')
    ]
    storage = Storage()
    assert storage.update(channel_id, results) == results


def test_storage_rep():
    channel_id = 1
    results = {
        ScrapeResult('res1', '22'),
        ScrapeResult('res2', '33')
    }
    storage = Storage()
    storage.update(channel_id, results)
    assert storage.update(channel_id, results) == []


def test_storage_diff():
    channel_id = 1
    results = {
        ScrapeResult('res1', '22'),
        ScrapeResult('res2', '33')
    }
    storage = Storage()
    storage.update(channel_id, results)

    results = {
        ScrapeResult('res1', '22'),
        ScrapeResult('res4', '44'),
    }

    assert storage.update(channel_id, results) == [ScrapeResult('res4', '44')]


def test_storage_empty():
    channel_id = 1
    results = {
        ScrapeResult('res1', '22'),
        ScrapeResult('res2', '33')
    }
    storage = Storage()
    storage.update(channel_id, results)
    assert storage.update(channel_id, []) == []
