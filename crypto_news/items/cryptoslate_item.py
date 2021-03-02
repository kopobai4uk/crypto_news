from .news_item import NewsItem
import scrapy


class CryptoSlateItem(NewsItem):
    name_of_subgroup = scrapy.Field(default=None)
