import scrapy
import re
from difficulty_scraper.items import EreterNetDifficulty

class EreternetSpiderSpider(scrapy.Spider):
    name = "ereternet_spider"
    allowed_domains = ["ereter.net"]
    start_urls = ["http://ereter.net/iidxsongs/analytics/combined/"]

    def parse(self, response):
        for music in response.css('body > div > div > div.col-md-9.content > div.scale-wrapper > table > tbody > tr'):
            yield EreterNetDifficulty(
                song_id         = re.sub('^.*/([0-9]+)/$', r'\1', music.css('td:nth-child(2) > a::attr(href)').extract_first().strip()),
                name            = music.css('td:nth-child(2) > a::text').extract_first().strip(),
                difficulty      = re.sub('^\((.+)\)$', r'\1', music.css('td:nth-child(2) > a > span::text').extract_first().strip()),
                unofficial_diff = re.sub('^.*?([.0-9]+)$', r'\1', music.css('td:nth-child(1)::text').extract_first().strip()),
                ec_diff         = re.sub('^.*?([.0-9]+)$', r'\1', music.css('td:nth-child(3) > span::text').extract_first().strip()),
                hc_diff         = re.sub('^.*?([.0-9]+)$', r'\1', music.css('td:nth-child(4) > span::text').extract_first().strip()),
                exh_diff        = re.sub('^.*?([.0-9]+)$', r'\1', music.css('td:nth-child(5) > span::text').extract_first().strip()),
                ec_count        = music.css('td:nth-child(6) > span::text').extract_first().strip(),
                hc_count        = music.css('td:nth-child(7) > span::text').extract_first().strip(),
                exh_count       = music.css('td:nth-child(8) > span::text').extract_first().strip()
            )

