import scrapy
from crypto_news.items import BitcoinMagazineItem
import datetime


class BitcoinMagazineSpider(scrapy.Spider):

    name = 'bitcoin_magazine_spider'
    start_urls = ['https://bitcoinmagazine.com/']

    def parse(self, response, **kwargs):
        url_to_articles = response.xpath('//ul[contains(@class, "sub-menu ")]'
                                         '/li/a/@href').get()
        yield response.follow(url_to_articles, self.parse_lise_of_news_links)

    def parse_lise_of_news_links(self, response):
        list_urls_to_news = response.xpath(
            '//div[contains(@class, "post-title")]'
            '/h5/a/@href').getall()
        list_dates_post = response.xpath(
            '//aside[contains(@class, "thb-post-bottom")]'
            '/ul/li[contains(@class,"post-date")]/text()').getall()
        for counter in range(0, len(list_urls_to_news)-1):
            self.date_filter(list_dates_post[counter])
            yield response.follow(list_urls_to_news[counter], self.pares_news)

        next_page = response.xpath(
            '//nav[contains(@class, "navigation pagination")]'
            '/div[contains(@class,"nav-links")]'
            '/a[contains(@class, "next page-numbers")]/@href')
        if next_page is not None:
            response.follow(next_page, self.parse_lise_of_news_links)

    def date_filter(self, date):
        clean_date = datetime.datetime.strptime(
            date.strip(), '%B %d, %Y').date()
        if (datetime.datetime.now().date() - clean_date).days > int(self.days):
            raise scrapy.exceptions.IgnoreRequest('incorrect date')

    def pares_news(self, response):
        news_item = BitcoinMagazineItem()
        news_item['main_url'] = self.start_urls[0]
        news_item['name_of_group'] = "Bitcoin"
        news_item['name_of_subgroup'] = response.xpath(
            '//div[contains(@class, "post-title-container")]'
            '/aside[contains(@class,"post-category post-detail-category")]'
            '/a/text()').get()
        news_item['title'] = response.xpath(
            '//div[contains(@class, "post-title-container")]'
            '/header[contains(@class, "post-title entry-header")]'
            '/h1/text()').get().strip()
        news_item['authors'] = []
        news_item['authors'].append(response.xpath(
            '//div[contains(@class,"author-and-date")]'
            '/div[contains(@class, "post-author")]'
            '/a/text()').get())
        news_item['date'] = datetime.datetime.strptime(response.xpath(
            '//div[contains(@class,"author-and-date")]'
            '/div[contains(@class, "thb-post-date")]/text()').get().strip(),
                                                '%B %d, %Y').date()
        news_item['text'] = response.xpath(
            '//div[contains(@class,"post-content-container")]'
            '/div[contains(@class, "post-content entry-content")]'
            '/*[self::p or self::h2]/text()').getall()
        yield news_item


