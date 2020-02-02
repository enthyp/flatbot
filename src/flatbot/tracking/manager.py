class BadRequest(Exception):
    pass


class Manager:
    def __init__(self, tracker_factory, config):
        self.config = config
        self.tracker_factory = tracker_factory
        self.url2id = {}
        self.trackers = {}
        # TODO: bootstrap from DB

    async def track(self, uid, url):
        tracker_id = self.url2id.get(url, None)
        if not tracker_id:
            tracker = self.tracker_factory.get(url)
            self.trackers[tracker.id] = tracker
        else:
            tracker = self.trackers[tracker_id]

        tracker.add(uid)
        return tracker.id

    async def untrack(self, uid, url):
        tracker_id = self.url2id.get(url, None)
        if not tracker_id:
            raise BadRequest()

        tracker = self.trackers[tracker_id]
        try:
            tracker.remove(uid)
            if not tracker.active:
                await tracker.cancel()
                del self.url2id[url]
                del self.trackers[tracker_id]
        except:
            raise BadRequest()

    async def cancel_tasks(self):
        for t in self.trackers.values():
            await t.cancel()

        self.url2id = {}
        self.trackers = {}

    async def handle_updates(self):
        pass

    async def on_error(self, channel_id, url):
        channel = self.channels[channel_id]

        if not channel.cancelled:
            await channel.cancel()

        del self.url2id[url]
        del self.channels[channel_id]
