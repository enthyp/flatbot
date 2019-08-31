import re
import asyncio


class Scrape:
    def __init__(self, base_url, span, freq):
        self.base_url = base_url
        self.timespan = span  # in minutes
        self.freq = freq  # in minutes


class Scheduler:
    scraper_map = {
        'gumtree': GumtreeScraper,
    }

    def __init__(self, config, notifier_queue):
        self.conf = config
        self.notif_queue = notifier_queue
        self.tasks = []
        self.matcher = re.compile(r'^(https://)?(www\.)?(?P<site>\w*)\.')

    def enqueue(self, scrape):
        scraper_cls = self._choose_scraper(scrape.base_url)
        scraper = scraper_cls(scrape.base_url, scrape.span, self.notif_queue)

        task = asyncio.create_task(self._periodic(scraper.run, freq))
        self.tasks.append(task)

    @staticmethod
    async def _periodic(func, freq):
        while True:
            await func()
            await asyncio.sleep(freq * 60)

    def _choose_scraper(self, url):
        match = self.matcher.search(url)
        if match:
            site = match['site']
            return self.scraper_map.get(site, None)
        else:
            return None

