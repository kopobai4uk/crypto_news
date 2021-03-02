import scrapy
from .news_item import NewsItem


class CoinDeskItem(NewsItem):
    name_of_subgroup = scrapy.Field()
