import base64
import os
import sys
import traceback as tb
import yaml
from cryptography import fernet

import asyncio
import firebase_admin
from aiohttp import web
from aiohttp_security import SessionIdentityPolicy, setup as setup_security
from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from flatbot import db, config
from flatbot.api.auth import DumbAuthorizationPolicy
from flatbot.api.routes import setup_routes
from flatbot.api.ssl import ssl_context
from flatbot.bot.notifications import Notifier
from flatbot.bot.scheduler import Scheduler


class FirebaseException(Exception):
    pass


def setup_firebase():
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        firebase_admin.initialize_app()
    else:
        raise FirebaseException(
            'One must provide credentials path in GOOGLE_APPLICATION_CREDENTIALS environment variable!'
        )

async def start_background_tasks(app, notifier, config):
    freq = config.notifier['frequency']

    async def notify():
        while True:
            await notifier.notify()
            await asyncio.sleep(60 * freq)

    app['result_listener'] = app.loop.create_task(notifier.listen())
    app['notifier'] = app.loop.create_task(notify())


def setup_bot(app, config): 
    queue = asyncio.Queue(loop=app.loop, maxsize=config.notifier['queue_size'])
    notifier = Notifier(app.loop, queue)
    
    scheduler = Scheduler(config, queue)    
    app['scheduler'] = scheduler

    async def start_background_wrapper(app):
        await start_background_tasks(app, notifier, config)
 
    app.on_startup.append(start_background_wrapper)


def setup_api(app):
    # Setup session storage.
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    setup_session(app, EncryptedCookieStorage(secret_key))
    
    # Load registered users into memory (for now).         
    app['users'] = db.get_users()

    # Setup database and DB-based authorization policy (in the future).
    # db_pool = await asyncpg.create_pool(database='', user='')
    # app['db_pool'] = db_pool

    setup_security(app, SessionIdentityPolicy(), DumbAuthorizationPolicy(app['users']))
    setup_routes(app)


def main():
    setup_firebase()

    conf = config.Config()
    app = web.Application() 
    setup_api(app)
    setup_bot(app, conf)

    context = ssl_context()
    web.run_app(app, host=conf.host, ssl_context=context)


if __name__ == '__main__':
    main()

