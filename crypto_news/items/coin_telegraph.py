import scrapy
from w3lib.html import remove_tags
from itemloaders.processors import Join, MapCompose, TakeFirst


class CoinTelegraphNews(scrapy.Item):
    title = scrapy.Field(input_processor=MapCompose(remove_tags),
                         output_processor=Join(), )
    author = scrapy.Field(input_processor=MapCompose(remove_tags),
                          output_processor=Join(), )
    date = scrapy.Field(input_processor=MapCompose(remove_tags),
                        output_processor=Join(), )
    text = scrapy.Field(input_processor=MapCompose(remove_tags),
                        output_processor=Join(), )
