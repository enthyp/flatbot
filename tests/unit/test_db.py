from aiohttp import web

from flatbot.config import Config
from flatbot.db import setup as setup_db


async def test_setup(config_path):
    app = web.Application()
    config = Config(config_path('config_full.yml'))
    await setup_db(app, config)
