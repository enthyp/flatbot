from aiohttp import web
from aiohttp_security import (
    remember, forget, authorized_userid,
    check_permission, check_authorized,
)

from flatbot.api.auth import check_credentials


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

    try:
        login, pwd = form['url'], form['password']
    except KeyError:
        raise web.HTTPBadRequest()    


    scheduler = request.app['scheduler']

    scheduler.enqueue()
    raise web.HTTPOk()


async def handle_delete(request):
    raise web.HTTPOk()

