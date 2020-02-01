from flatbot.api.handlers import (
    handle_login, handle_logout,
    handle_sub, handle_unsub
)


def setup_routes(app):
    app.router.add_post('/login', handle_login)
    app.router.add_get('/logout', handle_logout)
    app.router.add_post('/subscribe', handle_sub)
    app.router.add_post('/unsubscribe', handle_unsub)
