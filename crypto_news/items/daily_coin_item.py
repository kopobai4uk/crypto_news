from .news_item import NewsItem
from itemloaders.processors import MapCompose
import scrapy


class DailyCoinNewsItem(NewsItem):
    authors = scrapy.Field(
        output_processor=MapCompose(str.strip),
    )
