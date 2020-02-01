import argparse
from aiohttp import web

from flatbot.api import setup as setup_api
from flatbot.api.ssl import ssl_context
from flatbot.bot import setup as setup_bot
from flatbot.bot.notifications import setup as setup_firebase
from flatbot.config import Config
from flatbot.db import setup as setup_db


def main(config_path):
    setup_firebase()

    conf = Config(config_path) if config_path else Config()
    app = web.Application()

    db = setup_db(app, conf)
    setup_api(app, db)
    setup_bot(app, db, conf)

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
