import os
import pytest

from flatbot.config import Config
from flatbot.db.model import Advertisement, Site
from flatbot.db.storage import get_storage, Storage
from flatbot.tracking.manager import Manager
from flatbot.tracking.scrapers import BaseScraper


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
def storage(loop, config):
    async def _storage(config_file):
        storage = await get_storage(config(config_file))
        yield storage
        await storage.close()
    return _storage


@pytest.fixture
def site():
    ad1 = Advertisement('url/ad1', 'ad1')
    ad2 = Advertisement('url/ad2', 'ad2')
    site = Site('url', {ad1, ad2})
    return site


@pytest.fixture
def mock_storage(mocker):
    storage = mocker.Mock(spec=Storage)
    return storage


@pytest.fixture
def mock_scraper(mocker):
    scraper = mocker.Mock(spec=BaseScraper)
    return scraper


@pytest.fixture
def mock_manager(mocker):
    manager = mocker.Mock(spec=Manager)
    return manager


# Helper for mocking coroutines.
@pytest.fixture
def async_return():
    async def _async_return(value):
        return value
    return _async_return
