import os
import sys
import traceback as tb
import yaml

import asyncio
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


def setup_bot(app, loop):
    config = config.Config() 
    queue = asyncio.Queue(loop=loop, maxsize=100)
    notifier = Notifier(queue)
    scheduler = Scheduler(config, queue)
    
    app['scheduler'] = scheduler
    app.on_startup.append(...) 

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

    setup_security(app, SessionIdentityPolicy(), DumbAuthorizationPolicy(users))
    setup_routes(app)


def main():
    setup_firebase()

    loop = asyncio.get_event_loop()
    app = web.Application(loop=loop) 
    setup_api(app)
    setup_bot(app, loop)

    ssl_context = ssl_context()
    web.run_app(app, host='192.168.100.106', ssl_context=ssl_context)


if __name__ == '__main__':
    main()

