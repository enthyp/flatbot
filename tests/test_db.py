import logging
import pytest
from aiohttp import web

from flatbot.config import Config
from flatbot.db.storage import setup as setup_db, get_storage
from flatbot.db.model import Advertisement, Site


@pytest.mark.slow
async def test_setup(config_path):
    app = web.Application()
    config = Config(config_path('config_full.yml'))
    await setup_db(app, config)


@pytest.mark.slow
async def test_get_update_site(config_path):
    config = Config(config_path('config_full.yml'))
    storage = await get_storage(config)

    ad1 = Advertisement('url/ad1', 'ad1')
    ad2 = Advertisement('url/ad2', 'ad2')
    site = Site('url', [ad1, ad2])

    try:
        await storage.update_site('url', site)
        site_stored = await storage.get_site('url')
        assert site_stored == site
        logging.debug([site_stored, site])
    finally:
        storage.close()
