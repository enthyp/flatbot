from login.handlers import (
    handle_login, handle_add,
    handle_add, handle_delete
)


def setup_routes(app):
    app.router.add_post('/login', handle_login)
    app.router.add_get('/logout', handle_logout)
    app.router.add_post('/add', handle_add)
    app.router.add_post('/delete', handle_delete)

