import os
import pytest

from flatbot.config import Config


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
