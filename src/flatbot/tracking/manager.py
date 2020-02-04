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
        # TODO: bootstrap from DB

    async def track(self, uid, url):
        tracker_id = self.url2id.get(url, None)
        if not tracker_id:
            try:
                tracker = self.tracker_factory.get(url)
                self.trackers[tracker.id] = tracker
            except UnhandledURL:
                raise
        else:
            tracker = self.trackers[tracker_id]

        tracker.add(uid)
        return tracker.id

    async def untrack(self, login, url):
        tracker_id = self.url2id.get(url, None)
        if not tracker_id:
            raise BadRequest()

        tracker = self.trackers[tracker_id]
        try:
            tracker.remove(login)
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

    async def handle_updates(self, id, updates):
        # TODO: turn them into a message!
        self.notifier.notify(id, updates)
