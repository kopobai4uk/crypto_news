import scrapy
from scrapy.loader import ItemLoader
from crypto_news.items import BitcoinMagazineItem
import datetime


class BitcoinMagazineSpider(scrapy.Spider):

    name = 'bitcoin_magazine_spider'
    start_urls = ['https://bitcoinmagazine.com/']

    def parse(self, response, **kwargs):
        url_to_articles = response.xpath('//ul[contains(@class, "sub-menu ")]'
                                         '/li/a/@href').get()
        yield response.follow(url_to_articles,
                              self.parse_lise_of_news_links
                              )

    def parse_lise_of_news_links(self, response):
        list_urls_to_news = response.xpath(
            '//div[contains(@class, "post-title")]'
            '/h5/a/@href'
        ).getall()
        list_dates_post = response.xpath(
            '//aside[contains(@class, "thb-post-bottom")]'
            '/ul/li[contains(@class,"post-date")]/text()'
        ).getall()
        for counter in range(0, len(list_urls_to_news)-1):
            self.date_filter(list_dates_post[counter])
            yield response.follow(list_urls_to_news[counter],
                                  self.pares_news
                                  )

        next_page = response.xpath(
            '//nav[contains(@class, "navigation pagination")]'
            '/div[contains(@class,"nav-links")]'
            '/a[contains(@class, "next page-numbers")]/@href'
        )
        if next_page is not None:
            response.follow(next_page,
                            self.parse_lise_of_news_links
                            )

    def date_filter(self, date):
        clean_date = datetime.datetime.strptime(
            date.strip(), '%B %d, %Y').date()
        if (datetime.datetime.now().date() - clean_date).days > int(self.days):
            raise scrapy.exceptions.IgnoreRequest('incorrect date')

    def pares_news(self, response):
        news_item = ItemLoader(item=BitcoinMagazineItem(),
                               response=response)

        news_item.add_value('main_url', self.start_urls[0])
        news_item.add_value('name_of_group', "Bitcoin")
        news_item.add_xpath(
            'name_of_subgroup',
            '//div[contains(@class, "post-title-container")]'
            '/aside[contains(@class,"post-category post-detail-category")]'
            '/a/text()',
            TakeFirst(),
        )
        news_item.add_xpath(
            'title',
            '//div[contains(@class, "post-title-container")]'
            '/header[contains(@class, "post-title entry-header")]'
            '/h1/text()',
        )
        news_item.add_xpath(
            'authors',
            '//div[contains(@class,"author-and-date")]'
            '/div[contains(@class, "post-author")]/a/text()'
        )
        news_item.add_value(
            'date',
            self.date_to_iso(
                response.xpath(
                    '//div[contains(@class,"author-and-date")]'
                    '/div[contains(@class, "thb-post-date")]/text()'
                ).get()
            )
        )

        news_item.add_xpath(
            'text',
            '//div[contains(@class, "thb-post-share-container")]'
            '/div[contains(@class, "post-content-container")]'
            '//div[contains(@class, "post-content entry-content")]',
            TakeFirst()
        )
        yield news_item.load_item()

    @staticmethod
    def date_to_iso(date):
        return datetime.datetime.strptime(date.strip(), '%B %d, %Y')\
            .isoformat()
