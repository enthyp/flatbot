from flatbot.api.handlers import (
    handle_login, handle_logout,
    handle_track, handle_untrack
)


def setup_routes(app):
    app.router.add_post('/login', handle_login)
    app.router.add_post('/logout', handle_logout)
    app.router.add_post('/track', handle_track)
    app.router.add_post('/untrack', handle_untrack)
