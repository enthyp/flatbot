import logging
import sys
from aiohttp import web

from flatbot.api import setup_api
from flatbot.api.ssl import ssl_context
from flatbot.tracking import setup_bot
from flatbot.config import Config
from flatbot.db.storage import setup_db
from flatbot.notifications import setup_notifications

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def main():
    conf = Config()
    app = web.Application()

    setup_db(app, conf)
    setup_notifications(app)
    setup_api(app)
    setup_bot(app, conf)
    context = ssl_context(conf)
    if context:
        logging.info('Running with SSL on port {}.'.format(conf.port))
        web.run_app(app, port=conf.port, ssl_context=context)
    else:
        logging.info('Running without SLL on port {}.'.format(conf.port))
        web.run_app(app, port=conf.port)


if __name__ == '__main__':
    main()
