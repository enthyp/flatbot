from aiohttp import web
from aiohttp_security import (
    remember, forget, check_authorized,
    authorized_userid
)

from flatbot.api.auth import check_credentials
from flatbot.tracking.manager import BadRequest, ServerError


async def handle_login(request):
    form = await request.post()
    try:
        login, pwd = form['login'], form['password']
    except KeyError:
        raise web.HTTPBadRequest()    

    print("LOGIN: " + login, pwd)
    storage = request.app['storage']
    if await check_credentials(storage, login, pwd):
        response = web.HTTPOk()
        await remember(request, response, login)
        raise response
    else:
        raise web.HTTPUnauthorized()


async def handle_logout(request):
    response = web.HTTPOk()
    await forget(request, response) 
    raise response


async def handle_track(request):
    await check_authorized(request)
    login = await authorized_userid(request)

    form = await request.post()
    try:
        url = form['base_url']
    except KeyError:
        raise web.HTTPBadRequest()    

    print("SUBSCRIBE: " + url)
    manager = request.app['manager']
    try:
        tracker_id = await manager.track(login, url)
        return web.Response(text=str(tracker_id))
    except BadRequest:
        raise web.HTTPBadRequest()
    except ServerError:
        raise web.HTTPInternalServerError()


async def handle_untrack(request):
    await check_authorized(request)
    login = await authorized_userid(request)

    form = await request.post()
    try:
        url = form['base_url']
    except KeyError:
        raise web.HTTPBadRequest()

    print("UNSUBSCRIBE: " + url)
    manager = request.app['manager']
    try:
        await manager.untrack(login, url)
        raise web.HTTPOk()
    except BadRequest:
        raise web.HTTPBadRequest()
    except ServerError:
        raise web.HTTPInternalServerError()
