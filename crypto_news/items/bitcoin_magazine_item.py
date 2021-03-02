from .news_item import NewsItem
import scrapy


class BitcoinMagazineItem(NewsItem):
    name_of_subgroup = scrapy.Field()
