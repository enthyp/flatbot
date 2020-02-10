import os
import yaml
import warnings


class Config:
    def __init__(self):
        path = os.getenv('CONFIG_PATH')
        conf_dict = self._get_conf(path)
        self.host = conf_dict.get('host', '0.0.0.0')
        self.port = conf_dict.get('port', 84443)

        self.db = self._get_db(conf_dict)
        self.scraper = self._get_scraper(conf_dict)

        self.ssl_path = conf_dict.get('ssl_path', None)

    @staticmethod
    def _get_conf(config_path):
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

    @staticmethod
    def _get_db(config):
        default_db = {
            'name': 'db',
            'user': 'postgres',
            'password': 'postgres',
            'host': '0.0.0.0',
            'port': 5432
        }

        db_conf = config.get('db', {})
        default_db.update(db_conf)
        try:
            int(default_db['port'])
        except ValueError:
            raise ValueError('Invalid value in database configuration.')

        return default_db
    
    @staticmethod
    def _get_scraper(config):
        default_scraper = {
            'frequency': 5,
            'item_limit': 100,
        }

        scrap_conf = config.get('scraper', {})
        default_scraper.update(scrap_conf) 
        try:
            [int(v) for k, v in default_scraper.items()]
        except ValueError:
            raise ValueError('Invalid value in scraper configuration.')

        return default_scraper
