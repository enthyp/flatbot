import aiohttp
import re
from lxml import etree

from flatbot.db.model import Site, Advertisement


class UnhandledURL(Exception):
    pass


class BaseScraper:
    def __init__(self, conf):
        self.item_limit = conf.scraper['item_limit']

    class SpanExceeded(Exception):
        pass

    async def run(self, url):
        async with aiohttp.ClientSession() as session:
            site = Site(url, set())
            ads = set()
            next_page_available = True

            while next_page_available and len(ads) < self.item_limit:
                async with (await session.get(url)) as response:
                    html = await response.text()

                    page = self.parse(html)
                    items = self.get_items(page)

                    try:
                        for item in items:
                            if len(ads) >= self.item_limit:
                                break

                            ad = self.parse_item(item)
                            if ad:
                                ads.add(ad)

                        url = self.next_page(page)
                        if not url:
                            next_page_available = False
                    except BaseScraper.SpanExceeded:
                        break
        site.ads = ads
        return site

    @staticmethod
    def parse(html):
        raise NotImplementedError

    @staticmethod
    def next_page(site):
        raise NotImplementedError

    @staticmethod
    def get_items(site):
        raise NotImplementedError

    def parse_item(self, node):
        """Return an Advertisement."""
        raise NotImplementedError


class GumtreeScraper(BaseScraper):
    @staticmethod
    def parse(html):
        return etree.fromstring(html, etree.HTMLParser())

    @staticmethod
    def next_page(site):
        url = site.xpath('//div[@class="desktop-pagination"]/span[@class="pag-box"]/a/@href')
        return url

    @staticmethod
    def get_items(site):
        tiles = site.xpath('//div[@class="tileV1"]')
        return tiles

    def parse_item(self, node):
        title = node.xpath('./div[@class="title"]/a/text()')
        price = node.xpath('./div[@class="info"]/span[@class="price-text"]//text()')
        url = node.xpath('./div[@class="title"]/a')
        # date = node.xpath('./div[@class="info"]/div[@class="creation-date"]//text()')

        if title and price and url:
            content = '{}\n{}'.format(title[0].strip(), price[0].strip())
            url = url[0].get('href')
            url = 'https://www.gumtree.pl' + url
            return Advertisement(url, content)
        else:
            return None


matcher = re.compile(r'^(https://)?(www\.)?(?P<site>\w*)\.')
scrapers = {
    'gumtree': GumtreeScraper,
}


def get_scraper(url):
    match = matcher.search(url)

    try:
        site = match['site']
        return scrapers[site]
    except (KeyError, TypeError):
        raise UnhandledURL
