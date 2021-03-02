from .news_item import NewsItem
import scrapy
from itemloaders.processors import Join, MapCompose, TakeFirst


class CryptoSlateItem(NewsItem):
    name_of_subgroup = scrapy.Field(default=None)
    name_of_group = scrapy.Field(
        input_processor=MapCompose(str.strip),
    )
    authors = scrapy.Field(
        input_processor=MapCompose(str.strip),
    )
