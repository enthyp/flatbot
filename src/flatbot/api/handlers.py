from aiohttp import web
from aiohttp_security import (
    remember, forget, check_authorized,
    authorized_userid
)

from flatbot.api.auth import check_credentials
from flatbot.tracking.tracker import UnhandledURL, BadRequest


async def handle_login(request):
    form = await request.post()
    try:
        login, pwd = form['login'], form['password']
    except KeyError:
        raise web.HTTPBadRequest()    

    print("LOGIN: " + login, pwd)
    users = request.app['users']
    if await check_credentials(users, login, pwd):
        response = web.HTTPOk()
        await remember(request, response, login)
        raise response
    else:
        raise web.HTTPUnauthorized()


async def handle_logout(request):
    response = web.HTTPOk()
    await forget(request, response) 
    raise response


async def handle_sub(request):
    await check_authorized(request)
    uid = await authorized_userid(request)

    form = await request.post()
    try:
        url = form['base_url']
    except KeyError:
        raise web.HTTPBadRequest()    

    print("SUBSCRIBE: " + url)
    service = request.app['tracking']
    try:
        channel_id = service.track(uid, url)
        return web.Response(text=channel_id)
    except UnhandledURL:
        raise web.HTTPBadRequest()


async def handle_unsub(request):
    await check_authorized(request)
    uid = await authorized_userid(request)

    form = await request.post()
    try:
        url = form['base_url']
    except KeyError:
        raise web.HTTPBadRequest()

    print("UNSUBSCRIBE: " + url)
    service = request.app['tracking']
    try:
        await service.untrack(uid, url)
        raise web.HTTPOk()
    except BadRequest:
        raise web.HTTPBadRequest()
