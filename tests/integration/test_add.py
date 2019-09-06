import pytest
import asyncio
from aiohttp import web
from flatbot.__main__ import setup_api, setup_bot
from flatbot.config import Config


@pytest.fixture
def client(aiohttp_client, loop):
    app = web.Application()
    conf = Config()
    setup_api(app)
    setup_bot(app, conf)

    client = aiohttp_client(app)
    return loop.run_until_complete(client)


async def test_add(aiohttp_client):
    app = web.Application()
    conf = Config()
    setup_api(app)
    setup_bot(app, conf)

    client = await aiohttp_client(app)
    
    data = {'login': 'kuba', 'password': 'haslo'}
    resp = await client.post('/login', data=data)
    assert resp.status == 200

    data = {
        'base_url': 'https://www.gumtree.pl/s-pokoje-do-wynajecia/krakow/v1c9000l3200208p1?pr=,900',
    }
    resp = await client.post('/add', data=data, cookies=resp.cookies)
    assert resp.status == 200
    await asyncio.sleep(3)
