import argparse
from aiohttp import web

from flatbot.api import setup_api
from flatbot.api.ssl import ssl_context
from flatbot.tracking import setup_bot
from flatbot.config import Config
from flatbot.db.storage import setup_db
from flatbot.notifications import setup as setup_notifications


def main(config_path):
    conf = Config(config_path) if config_path else Config()
    app = web.Application()

    setup_db(app, conf)
    setup_notifications(app)
    setup_api(app)
    setup_bot(app, conf)

    context = ssl_context(conf)
    web.run_app(app, host=conf.host, port=conf.port, ssl_context=context)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config',
                        help='optional path to config_full.yml file (default: ../../config_full.yml)')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    main(args.config)
