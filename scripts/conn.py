import psycopg2
from contextlib import contextmanager

from flatbot.config import Config


@contextmanager
def get_connection():
    config = Config()
    db_config = config.db
    connection = psycopg2.connect(database=db_config['name'],
                                  user=db_config['user'],
                                  password=db_config['password'],
                                  host=db_config['host'],
                                  port=db_config['port'])
    try:
        yield connection
    finally:
        connection.close()
