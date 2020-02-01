import os
import pytest

from flatbot.config import Config


root_dir = os.path.dirname(os.path.abspath(__file__))
config_dir_path = os.path.join(root_dir, 'config_files')


@pytest.fixture
def config():
    def _config(file=None):
        if file:
            config_path = os.path.join(config_dir_path, file)
            return Config(config_path)
        else:
            return Config('')

    return _config
