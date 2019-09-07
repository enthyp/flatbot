from aiohttp import web
from aiohttp_security import (
    remember, forget, check_authorized,
    authorized_userid
)

from flatbot.api.auth import check_credentials
from flatbot.bot.scheduler import UnhandledUrl, BadRequest


async def handle_login(request):
    form = await request.post()
    try:
        login, pwd = form['login'], form['password']
    except KeyError:
        raise web.HTTPBadRequest()    

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


async def handle_add(request):
    await check_authorized(request)
    uid = await authorized_userid(request)

    form = await request.post()
    try:
        url = form['base_url']
    except KeyError:
        raise web.HTTPBadRequest()    

    scheduler = request.app['scheduler']
    try:
        channel_id = scheduler.enqueue(uid, url)
        return web.Response(text=channel_id)
    except UnhandledUrl:
        raise web.HTTPBadRequest()


async def handle_delete(request):
    await check_authorized(request)
    uid = await authorized_userid(request)

    form = await request.post()
    try:
        url = form['base_url']
    except KeyError:
        raise web.HTTPBadRequest()

    scheduler = request.app['scheduler']
    try:
        await scheduler.remove(uid, url)
        raise web.HTTPOk()
    except BadRequest:
        raise web.HTTPBadRequest()
