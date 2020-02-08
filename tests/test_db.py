import logging
import pytest
from aiohttp import web

from flatbot.db.storage import setup as setup_db
from flatbot.db.model import Advertisement, Site

# TODO: test should clean up after themselves?
# TODO: need to figure out some way of setting up test DB automatically...


@pytest.mark.slow
async def test_setup(config):
    app = web.Application()
    await setup_db(app, config('config_full.yml'))


@pytest.mark.slow
async def test_create_site(storage):
    async for storage in storage('config_full.yml'):
        await storage.create_site('url')
        await storage.create_site('url')


@pytest.mark.slow
async def test_add_new_site(storage, site):
    async for storage in storage('config_full.yml'):
        await storage.update_site('url', site)
        site_stored = await storage.get_site('url')
        assert site_stored == site


@pytest.mark.slow
async def test_update_existing_site(storage, site):
    async for storage in storage('config_full.yml'):
        await storage.update_site('url', site)
        site.ads.add(Advertisement('url/ad3', 'ad3'))
        await storage.update_site('url', site)

        site_stored = await storage.get_site('url')
        assert site == site_stored


@pytest.mark.slow
async def test_remove_site(storage):
    async for storage in storage('config_full.yml'):
        await storage.create_site('url')
        await storage.remove_site('url')
        logging.info(await storage.get_urls())
