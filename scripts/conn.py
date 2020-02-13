import psycopg2
from contextlib import contextmanager

from flatbot.config import Config


@contextmanager
def get_connection():
    config = Config()
    connection = psycopg2.connect(config.db_url)
    try:
        yield connection
    finally:
        connection.close()
