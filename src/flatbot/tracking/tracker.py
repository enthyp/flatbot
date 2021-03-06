import asyncio
import logging
import uuid

from flatbot.tracking.scrapers import get_scraper


class Tracker:
    def __init__(self, url, scraper, storage, config):
        self.id = str(uuid.uuid4())
        self.url = url
        self.freq = config.scraper['frequency']
        self.init_iter = config.scraper['burn_in']
        self.job = None

        self.storage = storage
        self.scraper = scraper
        self.update_handler = None  # should be set

    def run(self):
        self.job = asyncio.create_task(self._run())

    async def _run(self):
        await self.burn_in()

        try:
            while True:
                updated = await self.check_updates()
                if updated:
                    logging.info('Tracker {}: got some updates!'.format(self.id))
                    await self.update_handler.handle(self.id, updated)
                await asyncio.sleep(self.freq)
        except asyncio.CancelledError:
            pass

    async def burn_in(self):
        for _ in range(self.init_iter):
            await self.check_updates()

    async def check_updates(self):
        current = await self.scraper.run(self.url)
        prev = await self.storage.get_site(self.url)

        if current:
            if not current.ads.issubset(prev.ads):
                prev.ads.update(current.ads)  # TODO: should somehow remove stale ones too! o.O
                await self.storage.update_site(self.url, prev)
                return prev  # now current
            else:
                return None
        # TODO: handle scraper failure?

    async def add(self, login):
        await self.storage.add_track(self.url, login)

    async def remove(self, login):
        await self.storage.remove_track(self.url, login)

    async def cancel(self):
        # Site stays in the DB - we might want to remove VERY old
        # entries periodically, but apart from that results stay in the DB.
        if not self.cancelled:
            self.job.cancel()
            await self.job

    @property
    async def active(self):
        return await self.storage.is_tracked(self.url)

    @property
    def cancelled(self):
        return self.job.cancelled() if self.job else True


class TrackerFactory:
    def __init__(self, storage, config):
        self.config = config
        self.storage = storage

    async def get(self, url):
        scraper_cls = get_scraper(url)  # may raise
        scraper = scraper_cls(self.config)

        await self.storage.create_site(url)
        return Tracker(url, scraper, self.storage, self.config)

    async def get_all(self):
        # For initial DB bootstrap of the server?
        urls = await self.storage.get_active_urls()
        return await asyncio.gather(*[self.get(url) for url in urls])  # TODO: could use a single DB operation
