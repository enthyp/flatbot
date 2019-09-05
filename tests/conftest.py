import os
import pytest

dummy_config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'unit', 'test_config.yml')


@pytest.fixture
def config_path():
    return dummy_config_path
