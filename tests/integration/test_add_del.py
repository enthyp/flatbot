import asyncio
from aiohttp import web
from flatbot.__main__ import setup_api, setup_bot
from flatbot.config import Config


async def test_add_del_ok(aiohttp_client):
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

    data = {
        'base_url': 'https://www.gumtree.pl/s-pokoje-do-wynajecia/krakow/v1c9000l3200208p1?pr=,900',
    }
    resp = await client.post('/delete', data=data, cookies=resp.cookies)
    assert resp.status == 200
    await asyncio.sleep(1)


async def test_add_del_fail(aiohttp_client):
    app = web.Application()
    conf = Config()
    setup_api(app)
    setup_bot(app, conf)

    client = await aiohttp_client(app)

    data = {'login': 'kuba', 'password': 'haslo'}
    resp = await client.post('/login', data=data)
    assert resp.status == 200

    data = {
        'base_url': 'https://www.gumatree.pl/s-pokoje-do-wynajecia/krakow/v1c9000l3200208p1?pr=,900',
    }
    resp = await client.post('/delete', data=data, cookies=resp.cookies)
    assert resp.status == 400
    await asyncio.sleep(1)
