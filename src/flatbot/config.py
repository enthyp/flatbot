import logging
import os


class Config:
    def __init__(self):
        self.port = os.getenv('PORT', 8443)
        self.ssl_path = os.getenv('SSL_PATH', None)
        self.db_url = os.getenv('DATABASE_URL', None)
        self.url_limit = os.getenv('URL_LIMIT', 10)

        self.scraper = self._get_scraper()
        self._setup_google()

    @staticmethod
    def _get_scraper():
        freq = os.getenv('SCRAPER_FREQ', 300)
        item_limit = os.getenv('SCRAPER_ITEM_LIMIT', 10)
        burn_in = os.getenv('SCRAPER_BURN_IN', 5)
        scraper = {
            'frequency': float(freq),
            'item_limit': item_limit,
            'burn_in': burn_in
        }

        return scraper

    @staticmethod
    def _setup_google():
        # At least it works.
        cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not os.path.exists(cred_path):
            logging.info('Saving Google credentials...')
            google_cred = os.getenv('GOOGLE_CREDENTIALS')
            with open(cred_path, 'w') as cred_file:
                cred_file.write(google_cred)
