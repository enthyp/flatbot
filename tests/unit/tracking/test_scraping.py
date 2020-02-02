import time
import logging
import pytest
from flatbot.config import Config
from flatbot.tracking.scrapers import GumtreeScraper


@pytest.mark.slow
async def test_gumtree_scraper(config_path):
    url = 'https://www.gumtree.pl/s-pokoje-do-wynajecia/krakow/agh+pokoj+do+wynajecia+krakow/v1c9000l3200208q0p1'
    config = Config(config_path('config_full.yml'))
    scraper = GumtreeScraper(config)

    k = 5
    results = await scraper.run(url)

    while k > 0:
        new_results = await scraper.run(url)
        if new_results and results:
            assert new_results == results

        results = new_results
        k -= 1
        time.sleep(1)

    logging.debug(results)
