import asyncio
import uuid

from flatbot.bot.scraper import get_scraper, UnhandledURL


class BadRequest(Exception):
    pass


class Channel:
    def __init__(self, url, db, notifier, err_handler, config):
        self.id = str(uuid.uuid4())
        self.url = url

        scraper_cls = get_scraper(url)  # may raise
        self.scraper = scraper_cls(config)

        self.db = db
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
                diff = self.db.update(self.id, results)

                if diff:
                    await self.notifier.notify(self.id, diff)
                await asyncio.sleep(self.freq * 3)
        except asyncio.CancelledError:
            pass
        except Exception:
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


class Manager:
    def __init__(self, db, notifier, config):
        self.db = db
        self.notifier = notifier
        self.config = config
        self.url2id = {}
        self.channels = {}

    async def subscribe(self, uid, url):
        channel_id = self.url2id.get(url, None)

        if not channel_id:
            try:
                channel = Channel(url, self.db, self.notifier, self, self.config)
                channel.run()
            except UnhandledURL:
                raise

            self.channels[channel.id] = channel
            self.url2id[url] = channel.id
        else:
            channel = self.channels[channel_id]

        channel.subscribe(uid)
        return channel.id

    async def unsubscribe(self, uid, url):
        channel_id = self.url2id.get(url, None)
        if channel_id:
            channel = self.channels[channel_id]
            channel.unsubscribe(uid)

            if not channel.active:
                await channel.cancel()
                del self.url2id[url]
                del self.channels[channel_id]
        else:
            raise BadRequest()


    async def cancel_tasks(self):
        for c in self.channels.values():
            await c.cancel()

        self.url2id = {}
        self.channels = {}

    async def on_error(self, channel_id, url):
        channel = self.channels[channel_id]

        if not channel.cancelled:
            await channel.cancel()

        del self.url2id[url]
        del self.channels[channel_id]
