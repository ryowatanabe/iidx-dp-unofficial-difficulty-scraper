import scrapy
import re
from difficulty_scraper.items import UnofficialDifficulty
import logging

class UnofficialDiffSpider(scrapy.Spider):
    name = "unofficial_diff"
    allowed_domains = ["zasa.sakura.ne.jp"]
    start_urls = ["https://zasa.sakura.ne.jp/dp/rank.php"]
    logger = logging.getLogger(__name__)
    difficulty_map = {
        'N' : 'NORMAL',
        'H' : 'HYPER',
        'A' : 'ANOTHER',
        'L' : 'LEGGENDARIA'
    }

    def parse(self, response):
        self.logger.setLevel(logging.DEBUG)

        current_version = response.css('.rank_form > tr:nth-child(1) > td:nth-child(2) > select > option:checked::attr(value)').extract_first().strip()

        return scrapy.FormRequest.from_response(response, 
            formdata={
            "env":f'{current_version}',
            "cat":"0",
            "mode":"p2",
            "offi":"0",
            "submit":"表示"
        }, callback=self.parsePost)

    def parsePost(self, response):
        for row in response.css('.rank_p2 > tr'):
            diff = row.css('td:first-child::text').extract_first()
            if not(diff is None):
                self.logger.debug(diff)
                for song in row.css('.rank_p2_inner a.music'):
                    song_id = re.sub('^music.php\?id\=([\-0-9]+)$', r'\1', song.css('a::attr(href)').extract_first().strip())
                    name = re.sub('\s\[[NHAL]\]$', '', song.css('span::text').extract_first().strip())
                    difficulty = self.difficulty_map[re.sub('^.*\s\[([NHAL])\]$', r'\1', song.css('span::text').extract_first().strip())]
                    yield UnofficialDifficulty(
                        song_id         = song_id,
                        name            = name,
                        difficulty      = difficulty,
                        unofficial_diff = diff
                    )
