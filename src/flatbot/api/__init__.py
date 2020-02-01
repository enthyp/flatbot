import base64
from cryptography import fernet

from aiohttp_security import SessionIdentityPolicy, setup as setup_security
from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from flatbot.api.auth import DBAuthorizationPolicy
from flatbot.api.routes import setup_routes


def setup(app, storage):
    # Setup session storage.
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    setup_session(app, EncryptedCookieStorage(secret_key))

    setup_security(app, SessionIdentityPolicy(), DBAuthorizationPolicy(storage))
    setup_routes(app)
