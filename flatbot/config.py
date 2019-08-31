import os
import yaml
import warnings
import firebase_admin
from flatbot.scraper import GumtreeScraper

ROOT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SSL_PATH = os.path.join(ROOT_PATH, 'ssl')
DATA_PATH = os.path.join(ROOT_PATH, 'data')
CONFIG_PATH = os.path.join(ROOT_PATH, 'config.yml')


class Config:
    def __init__(self):
        conf_dict = self._get_conf(CONFIG_PATH)
        self.host = config.get('host', '0.0.0.0')
        self.port = config.get('port', '84443')

    def _get_conf(self, config_path):
        try:
            with open(config_path, 'r') as config_file:
                config = yaml.safe_load(config_file)
                return config if config else {}
        except IOError:
            warnings.warn(
                'Could not open {} file. Using default values instead.'.format(config_path), 
                RuntimeWarning
            )
            return {}

