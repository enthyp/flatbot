import bcrypt
from aiohttp_security.abc import AbstractAuthorizationPolicy

# TODO: update both methods
# TODO: provide SQL scripts to setup tables and manage users
# an alternative would be to provide an admin endpoint - maybe some day

class DBAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, db):
        self.db = db

    async def authorized_userid(self, identity):
        if identity in self.users.keys():
            return identity
        else:
            return None

    async def permits(self, identity, permission, context=None):
        if identity is None:
            return False
        
        return identity in self.users.keys()


async def check_credentials(users, username, password):
    if username in users: 
        if bcrypt.checkpw(password.encode(), users[username].encode()):
            return True

    return False

