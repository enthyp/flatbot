import os
import pytest

from flatbot.config import Config
from flatbot.db.model import Advertisement, Site
from flatbot.db.storage import get_storage


root_dir = os.path.dirname(os.path.abspath(__file__))
config_dir_path = os.path.join(root_dir, 'config_files')


@pytest.fixture
def config_path():
    def _config_path(file):
        return os.path.join(config_dir_path, file)

    return _config_path


@pytest.fixture
def config(config_path):
    def _config(file):
        path = config_path(file)
        return Config(path)

    return _config


@pytest.fixture
def storage(loop):
    async def _storage(config):
        storage = await get_storage(config)
        yield storage
        await storage.close()
    return _storage


@pytest.fixture
def site():
    ad1 = Advertisement('url/ad1', 'ad1')
    ad2 = Advertisement('url/ad2', 'ad2')
    site = Site('url', [ad1, ad2])
    return site


@pytest.fixture
def storage():
    async def _storage(config):
        return await get_storage(config)
    return _storage
