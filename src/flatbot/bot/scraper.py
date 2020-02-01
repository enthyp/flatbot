import aiohttp
import re
from lxml import etree


class UnhandledURL(Exception):
    pass



class ScrapeResult:
    def __init__(self, name, price):
        self.name = name
        self.price = price
        
    def __str__(self):
        return 'price: {}'.format(self.price)

    def __members(self):
        return self.name, self.price

    def __eq__(self, other):
        return self.__members() == other.__members()

    def __hash__(self):
        return hash(self.__members())


class BaseScraper:
    def __init__(self, conf):
        self.item_limit = conf.scraper['item_limit']

    class SpanExceeded(Exception):
        pass

    async def run(self, url):
        async with aiohttp.ClientSession() as session:
            next_page_available = True
            results = []

            while next_page_available and len(results) < self.item_limit:
                async with (await session.get(url)) as response:
                    html = await response.text()

                    site = self.parse(html)
                    items = self.get_items(site)

                    try:
                        for item in items:
                            if len(results) >= self.item_limit:
                                break

                            item = self.parse_item(item)
                            if item:
                                results.append(item)

                        url = self.next_page(site)
                        if not url:
                            next_page_available = False
                    except BaseScraper.SpanExceeded:
                        break
        return results

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
        date = node.xpath('./div[@class="info"]/div[@class="creation-date"]//text()')

        if title and price and date:
            return ScrapeResult(title[0].strip(), price[0].strip())
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
    except KeyError:
        raise UnhandledURL
