import asyncio
import pytest
from aiohttp import web

from flatbot.api import setup as setup_api
from flatbot.db.storage import setup as setup_db
from flatbot.tracking.manager import Manager


# Just the API.
@pytest.mark.slow
async def test_add_remove(config, async_return, aiohttp_client, mocker):
    app = web.Application()
    conf = config('config_full.yml')
    await setup_db(app, conf)
    setup_api(app)

    mock_manager = mocker.Mock(spec=Manager)
    app['manager'] = mock_manager
    mock_manager.track.return_value = async_return(1)
    mock_manager.untrack.return_value = async_return(None)

    client = await aiohttp_client(app)
    
    data = {'login': 'kuba', 'password': 'haslo'}
    resp = await client.post('/login', data=data)
    assert resp.status == 200

    data = {
        'base_url': 'https://www.gumtree.pl/s-pokoje-do-wynajecia/krakow/v1c9000l3200208p1?pr=,900',
    }
    resp = await client.post('/track', data=data, cookies=resp.cookies)
    assert resp.status == 200

    resp = await client.post('/untrack', data=data, cookies=resp.cookies)
    assert resp.status == 200
    await asyncio.sleep(1)

    resp = await client.post('/logout')
    assert resp.status == 200

    mock_manager.track.assert_called_once_with('kuba', data['base_url'])
    mock_manager.untrack.assert_called_once_with('kuba', data['base_url'])
