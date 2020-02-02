import os
import pytest

root_dir = os.path.dirname(os.path.abspath(__file__))
config_dir_path = os.path.join(root_dir, 'config_files')


@pytest.fixture
def config_path():
    def _config_path(file):
        return os.path.join(config_dir_path, file)

    return _config_path
