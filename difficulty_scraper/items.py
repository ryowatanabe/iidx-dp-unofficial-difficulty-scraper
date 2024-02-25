# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class EreterNetDifficulty(scrapy.Item):
    song_id = scrapy.Field()
    name = scrapy.Field()
    difficulty = scrapy.Field()
    unofficial_diff = scrapy.Field()
    ec_diff = scrapy.Field()
    hc_diff = scrapy.Field()
    exh_diff = scrapy.Field()
    ec_count = scrapy.Field()
    hc_count = scrapy.Field()
    exh_count = scrapy.Field()

class DifficultyScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

