from datetime import datetime as dt

from flatbot.db.storage import DBError, InvalidOpError
from flatbot.tracking.scrapers import UnhandledURL


class ServerError(Exception):
    pass


class BadRequest(Exception):
    pass


class Manager:
    def __init__(self, tracker_factory, notifier, config):
        self.config = config
        self.tracker_factory = tracker_factory
        self.notifier = notifier
        self.url2id = {}
        self.trackers = {}

    async def bootstrap(self):
        trackers = await self.tracker_factory.get_all()
        for t in trackers:
            self.url2id[t.url] = t.id
            self.trackers[t.id] = t
            t.update_handler = self
            t.run()

    async def track(self, login, url):
        if len(self.trackers.keys()) >= self.config.url_limit:
            raise BadRequest()  # TODO: should somehow give a reason actually

        tracker_id = self.url2id.get(url, None)
        if not tracker_id:
            try:
                tracker = await self.tracker_factory.get(url)
                tracker.update_handler = self
                self.trackers[tracker.id] = tracker
                self.url2id[url] = tracker.id
                tracker.run()
            except UnhandledURL:
                raise BadRequest()
        else:
            tracker = self.trackers[tracker_id]

        try:
            await tracker.add(login)
        except InvalidOpError:
            raise BadRequest()
        except DBError:
            raise ServerError()

        return tracker.id

    async def untrack(self, login, url):
        tracker_id = self.url2id.get(url, None)
        if not tracker_id:
            raise BadRequest()

        tracker = self.trackers[tracker_id]
        try:
            await tracker.remove(login)
            if not tracker.active:
                await tracker.cancel()
                del self.url2id[url]
                del self.trackers[tracker_id]
        except InvalidOpError:
            raise BadRequest()
        except DBError:
            raise ServerError()

    async def cancel_tasks(self):
        for t in self.trackers.values():
            await t.cancel()

        self.url2id = {}
        self.trackers = {}

    async def handle(self, id, site):
        ads = {ad.url: ad.content for ad in site.ads}
        payload = {
            "site": site.url,
            "date": dt.strftime(dt.now(), '%Y:%M:%d %H:%M')
        }
        payload.update(ads)
        await self.notifier.notify(id, payload)
