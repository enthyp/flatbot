import pytest
from typing import NamedTuple

from flatbot.config import Config, DEFAULT_SSL_PATH


class MockConfig(NamedTuple):
    host: str
    port: int
    scraper: dict
    db: dict
    ssl_path: str


default_target = MockConfig(
    host='0.0.0.0',
    port=84443,
    scraper={
        'frequency': 5,
        'item_limit': 100
    },
    db={
        'name': 'db',
        'user': 'root',
        'password': 'root',
        'host': '0.0.0.0',
        'port': 5432
    },
    ssl_path=DEFAULT_SSL_PATH
)

full_target = MockConfig(
    host='192.168.100.106',
    port=8443,
    scraper={
        'frequency': 1,
        'item_limit': 3
    },
    db={
        'name': 'db',
        'user': 'root',
        'password': 'root',
        'host': '192.168.100.106',
        'port': 5432
    },
    ssl_path='./ssl'
)


def configs_equal(config, target):
    return all([
        config.__getattribute__(attr) == target.__getattribute__(attr)
        for attr in ['host', 'port', 'scraper', 'db', 'ssl_path']
    ])


def test_config_full(config_path):
    path = config_path('config_full.yml')
    conf = Config(path)
    assert configs_equal(conf, full_target)


def test_config_empty(config_path):
    path = config_path('config_empty.yml')
    conf = Config(path)
    assert configs_equal(conf, default_target)


def test_config_no_file(config_path):
    with pytest.warns(RuntimeWarning):
        path = config_path('blah')
        conf = Config(path)
        assert configs_equal(conf, default_target)
