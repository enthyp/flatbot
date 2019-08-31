import re
import aiohttp
from lxml import etree


class ScrapeResult:
    def __init__(self, name, price):
        self.name = name
        self.price = price
        
    def __str__(self):
        return 'price: {}'.format(self.price)


class BaseScraper:
    def __init__(self, base_url, span, result_queue):
        self.base_url = base_url
        self.timespan = span
        self.result_queue = result_queue
        self.item_limit = 100  # TODO: magic

    class SpanExceeded(Exception):
        pass

    async def run(self):
        async with aiohttp.ClientSession() as session:
            next_page_available = True
            url = self.base_url
            count = 0

            while next_page_available and count < self.item_limit:
                async with session.get(url) as response:
                    html = await response.text()

                    site = self.parse(html)
                    items = self.get_items(site)

                    try:
                        for item in items:
                            if count >= self.item_limit:
                                break

                            result = self.parse_item(item)
                            if result:
                                await self.result_queue.put(result)
                                count += 1
                        url = self.next_page(site)
                        if not url:
                            next_page_available = False
                    except SpanExceeded:
                        break

    @staticmethod
    def parse(html):
        raise NotImplementedError

    @staticmethod
    def next_page(site):
        raise NotImplementedError

    @staticmethod
    def get_items(site):
        raise NotImplementedError

    @staticmethod
    def parse_item(node):
        raise NotImplementedError


class GumtreeScraper(BaseScraper):
    def __init__(self, base_url, span, result_queue):
        super().__init__(base_url, span, result_queue)
        h_string = r'(?P<h>(?P<h_t>\d*)\s*godzin)'
        m_string = r'(?P<m>(?P<m_t>\d*)\s*minut)' 
        self.matcher = re.compile(h_string + r'|' + m_string)

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

    @staticmethod
    def parse_item(node):
        title = node.xpath('./div[@class="title"]/a/text()')
        price = node.xpath('./div[@class="info"]/span[@class="price-text"]//text()')
        posted = node.xpath('./div[@class="info"]/div[@class="creation-date"]//text()')
        if posted:
            
            minutes_ago = self._parse_posted(posted)
            if minutes_ago and minutes_ago > self.timespan:
                raise SpanExceeded()
 
        return ScrapeResult(title[0].strip(), price[0].strip())

    @staticmethod
    def _parse_posted(posted):
        match = self.matcher.search(posted)
        if not match:
            return None

        if match['h']:
            if match['h_t']:
                return int(match['h_t']) * 60
            else:
                return 60
        else:
            if match['m_t']:
                return int(match['m_t'])
            else:
                return 1

