import base64
from cryptography import fernet

from aiohttp import web
from aiohttp_security import SessionIdentityPolicy, setup as setup_security
from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from flatbot import config, db
from flatbot.api.auth import DumbAuthorizationPolicy
from flatbot.api.routes import setup_routes
from flatbot.api.ssl import ssl_context
from flatbot.bot.notifications import Notifier, setup_firebase
from flatbot.bot.scheduler import Scheduler


async def cleanup_background_tasks(app):
    await app['scheduler'].cancel_tasks()


def setup_bot(app, config):
    storage = db.Storage()
    notifier = Notifier()
    scheduler = Scheduler(storage, notifier, config)
    app['scheduler'] = scheduler
    app.on_cleanup.append(cleanup_background_tasks)


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
