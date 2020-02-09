from aiohttp import web
import os

from flatbot.api import setup_api
from flatbot.api.ssl import ssl_context
from flatbot.tracking import setup_bot
from flatbot.config import Config
from flatbot.db.storage import setup_db
from flatbot.notifications import setup_notifications


def main():
    config_path = os.getenv('CONFIG_PATH')
    conf = Config(config_path) if config_path else Config()
    app = web.Application()

    setup_db(app, conf)
    setup_notifications(app)
    setup_api(app)
    setup_bot(app, conf)

    context = ssl_context(conf)
    if context:
        web.run_app(app, host=conf.host, port=conf.port, ssl_context=context)
    else:
        web.run_app(app, host=conf.host, port=conf.port)


if __name__ == '__main__':
    main()
