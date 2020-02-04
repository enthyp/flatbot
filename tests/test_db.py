import logging
import pytest
from aiohttp import web

from flatbot.db.storage import setup as setup_db, get_storage
from flatbot.db.model import Advertisement, Site

# TODO: test should clean up after themselves?


@pytest.fixture
def site():
    ad1 = Advertisement('url/ad1', 'ad1')
    ad2 = Advertisement('url/ad2', 'ad2')
    site = Site('url', [ad1, ad2])
    return site


@pytest.fixture
async def storage(loop, config):
    storage = await get_storage(config('config_full.yml'))
    yield storage
    await storage.close()


@pytest.mark.slow
async def test_setup(config):
    app = web.Application()
    await setup_db(app, config('config_full.yml'))


@pytest.mark.slow
async def test_create_site(storage):
    await storage.create_site('url')
    await storage.create_site('url')


@pytest.mark.slow
async def test_add_new_site(storage, site):
    await storage.update_site('url', site)
    site_stored = await storage.get_site('url')
    assert site_stored == site


@pytest.mark.slow
async def test_update_existing_site(storage, site):
    await storage.update_site('url', site)
    site.ads.append(Advertisement('url/ad3', 'ad3'))
    await storage.update_site('url', site)

    site_stored = await storage.get_site('url')
    assert site == site_stored


@pytest.mark.slow
async def test_remove_site(storage):
    await storage.create_site('url')
    await storage.remove_site('url')
    logging.info(await storage.get_urls())
