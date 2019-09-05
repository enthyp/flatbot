import pytest

from aiohttp import web

from flatbot.__main__ import setup_api


@pytest.fixture
def client(aiohttp_client, loop):
    app = web.Application()
    setup_api(app)

    return loop.run_until_complete(aiohttp_client(app))


async def test_login_out(client):
    data = {'login': 'kuba', 'password': 'haslo'}
    resp = await client.post('/login', data=data)
    assert resp.status == 200

    resp = await client.get('/logout', cookies=resp.cookies)
    assert resp.status == 200

# TODO: needs much better tests! mock injection etc.