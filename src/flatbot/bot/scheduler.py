import re
import asyncio
import uuid

from flatbot.bot.scraper import GumtreeScraper


class UnhandledUrl(Exception):
    pass


class BadRequest(Exception):
    pass


class Channel:
    def __init__(self, url, scraper, storage, notifier, err_handler, config):
        self.id = str(uuid.uuid4())
        self.url = url
        self.scraper = scraper
        self.storage = storage
        self.notifier = notifier
        self.err_handler = err_handler
        self.clients = set()

        self.freq = config.scraper['frequency']
        self.job = None

    def run(self):
        self.job = asyncio.create_task(self._run())

    async def _run(self):
        try:
            while True:
                results = await self.scraper.run(self.url)
                diff = self.storage.update(self.id, results)

                if diff:
                    await self.notifier.notify(self.id, diff)
                await asyncio.sleep(self.freq * 3)
        except asyncio.CancelledError:
            pass
        except:
            await self.err_handler.on_error(self.id, self.url)

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


class Scheduler:
    scraper_map = {
        'gumtree': GumtreeScraper,
    }

    def __init__(self, storage, notifier, config):
        self.storage = storage
        self.notifier = notifier
        self.config = config
        self.channels = {}
        self.ids = {}
        self.matcher = re.compile(r'^(https://)?(www\.)?(?P<site>\w*)\.')

    def enqueue(self, uid, url):
        channel_id = self.ids.get(url, None)

        if not channel_id:
            cls = self._choose_scraper(url)
            if cls:
                scraper = cls(self.config)
                channel = Channel(url, scraper, self.storage, self.notifier, self, self.config)
                channel.run()
                self.channels[channel.id] = channel
                self.ids[url] = channel.id
            else:
                raise UnhandledUrl()
        else:
            channel = self.channels[channel_id]

        channel.subscribe(uid)
        return channel.id

    async def remove(self, uid, url):
        channel_id = self.ids.get(url, None)
        if channel_id:
            channel = self.channels[channel_id]
            channel.unsubscribe(uid)

            if not channel.active:
                await channel.cancel()
                del self.ids[url]
                del self.channels[channel_id]
        else:
            raise BadRequest()

    def _choose_scraper(self, url):
        match = self.matcher.search(url)
        if match:
            site = match['site']
            return self.scraper_map.get(site, None)
        else:
            return None

    async def cancel_tasks(self):
        for t in self.channels.values():
            await t.cancel()

        self.ids = {}
        self.channels = {}

    async def on_error(self, channel_id, url):
        channel = self.channels[channel_id]

        if not channel.cancelled:
            await channel.cancel()

        del self.ids[url]
        del self.channels[channel_id]
