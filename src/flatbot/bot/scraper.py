import aiohttp
from lxml import etree


class ScrapeResult:
    def __init__(self, name, price):
        self.name = name
        self.price = price
        
    def __str__(self):
        return 'price: {}'.format(self.price)


class BaseScraper:
    def __init__(self, base_url, conf):
        self.base_url = base_url
        self.item_limit = conf.scraper['item_limit']

    class SpanExceeded(Exception):
        pass

    async def run(self):
        async with aiohttp.ClientSession() as session:
            next_page_available = True
            url = self.base_url
            results = set()

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
                                results.add(item)

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
        
        if title and price: 
            return ScrapeResult(title[0].strip(), price[0].strip())
        else:
            return None        
