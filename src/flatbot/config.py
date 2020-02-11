import os


class Config:
    def __init__(self):
        self.port = os.getenv('PORT', 8443)
        self.ssl_path = os.getenv('SSL_PATH', None)
        self.google_cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', None)
        self.db = self._get_db()
        self.scraper = self._get_scraper()

    @staticmethod
    def _get_db():
        name = os.getenv('POSTGRES_DB', 'db')
        host = os.getenv('POSTGRES_HOST', 'postgres')
        port = os.getenv('POSTGRES_PORT', 5432)
        user = os.getenv('POSTGRES_USER', 'postgres')
        pwd = os.getenv('POSTGRES_PASSWORD', 'postgres')
        db = {
            'name': name,
            'host': host,
            'port': port,
            'user': user,
            'password': pwd,
        }

        return db
    
    @staticmethod
    def _get_scraper():
        freq = os.getenv('SCRAPER_FREQ', 300)
        item_limit = os.getenv('SCRAPER_ITEM_LIMIT', 10)
        url_limit = os.getenv('SCRAPER_URL_LIMIT', 10)
        scraper = {
            'frequency': float(freq),
            'item_limit': item_limit,
            'url_limit': url_limit
        }

        return scraper
