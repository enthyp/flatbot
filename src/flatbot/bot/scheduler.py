import re
import asyncio
import contextlib
import uuid

from flatbot.bot.scraper import GumtreeScraper


class UnhandledUrl(Exception):
    pass


class BadRequest(Exception):
    pass


class URLChannel:
    def __init__(self, id, scraper, storage, notifier, err_handler, config):
        self.id = id
        self.scraper = scraper
        self.storage = storage
        self.notifier = notifier
        self.err_handler = err_handler

        self.freq = config.scraper['frequency']
        self.clients = set()
        self.job = None

    def run(self):
        self.job = asyncio.create_task(self._run())

    async def _run(self):
        try:
            while True:
                results = await self.scraper.run()
                diff = self.storage.update(id, results)
                if diff:
                    await self.notifier.notify(self.id, results)
                await asyncio.sleep(self.freq * 5)
        except asyncio.CancelledError:
            pass
        except:
            self.err_handler.on_error(self.id)

    async def cancel(self):
        if self.job:
            self.job.cancel()
            await self.job

    def subscribe(self, uid):
        self.clients.add(uid)

    def unsubscribe(self, uid):
        self.clients.discard(uid)

    def active(self):
        return True if self.clients else False

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
        self.urls = {}
        self.matcher = re.compile(r'^(https://)?(www\.)?(?P<site>\w*)\.')

    def enqueue(self, uid, url):
        channel = self.channels.get(url, None)

        if not channel:
            cls = self._choose_scraper(url)
            if cls:
                scraper = cls(url, self.config)
                channel_id = str(uuid.uuid4())
                channel = URLChannel(channel_id, scraper, self.storage, self.notifier, self, self.config)
                channel.subscribe(uid)
                channel.run()
                self.channels[url] = channel
                self.urls[id] = url
            else:
                raise UnhandledUrl()

        return channel.id

    async def remove(self, uid, url):
        channel = self.channels.get(url, None)
        if channel:
            channel.unsubscribe(uid)
            if not channel.active():
                await channel.cancel()
                del channel
                del self.urls[channel.id]
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

    async def on_error(self, id):
        url = self.urls[id]
        task = self.channels[url]

        if not task.cancelled():
            await task.cancel()

        del self.channels[url]
        del self.urls[id]
