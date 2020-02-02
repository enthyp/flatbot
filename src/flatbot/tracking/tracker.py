import asyncio
import uuid

from flatbot.tracking.scrapers import get_scraper


class Tracker:
    def __init__(self, url, storage, manager, scraper, config):
        self.id = str(uuid.uuid4())
        self.url = url

        self.scraper = scraper

        self.storage = storage
        self.manager = manager
        self.clients = set()

        self.freq = config.scraper['frequency']
        self.job = None

    def run(self):
        self.job = asyncio.create_task(self._run())

    async def _run(self):
        try:
            while True:
                updates = self.check_updates()
                if updates:
                    self.manager.handle_updates(updates)
                await asyncio.sleep(self.freq * 60)
        except asyncio.CancelledError:
            pass

    async def check_updates(self):
        current = await self.scraper.run(self.url)
        prev = self.storage.get_site(self.url)

        if prev != current:
            self.storage.update_site(current, self.url)
            return current
        else:
            return None

    async def cancel(self):
        if not self.cancelled:
            self.job.cancel()
            await self.job

    def subscribe(self, uid):
        self.clients.add(uid)

    def unsubscribe(self, uid):
        self.clients.discard(uid)

    @property
    def active(self):
        return True if self.clients else False

    @property
    def cancelled(self):
        return self.job.cancelled() if self.job else True


class TrackerFactory:
    def __init__(self, db, notifier, config):
        self.config = config
        self.db = db

    def get(self, url):
        scraper_cls = get_scraper(url)  # may raise
        scraper = scraper_cls(self.config)

        # Get or create a Site.
        return Tracker(url)

    def get_all(self):
        # TODO: for DB bootstrapping the Manager
        # get all stored sites, get a Tracker for each
        return []
