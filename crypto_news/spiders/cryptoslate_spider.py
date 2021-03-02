import scrapy
import re
import datetime
from dateutil.relativedelta import relativedelta
from crypto_news.items import CryptoSlateItem


class CryptoSlateSpider(scrapy.Spider):

    name = 'cryptoslate'
    start_urls = ['https://cryptoslate.com/']

    def parse(self, response, **kwargs):
        list_of_category_links = response.xpath(
            '//div[contains(@id, "menu-navigation")]'
            '/div[contains(@id, "news")]'
            '/div[contains(@class, "menu-crypto-news-menu-container")]'
            '/ul[contains(@class,"menu")]/li/a/@href'
        )
        yield from response.follow_all(list_of_category_links,
                                       self.parse_list_of_links_news)

    def parse_list_of_links_news(self, response):
        list_of_posts_links = response.xpath(
            '//div[contains(@class,"container")]'
            '/div[contains(@class,"news-feed")]'
            '/div[contains(@class,"list-feed")]'
            '/div[contains(@class,"list-post clearfix")]'
            '/article/a/@href').getall()
        list_of_date_posts = response.xpath(
            '//div[contains(@class,"container")]'
            '/div[contains(@class,"news-feed")]'
            '/div[contains(@class,"list-feed")]'
            '/div[contains(@class,"list-post clearfix")]'
            '/article/div[contains(@class,"content")]'
            '/div/span[contains(@class,"post-meta")]'
            '/text()'
        ).re(r'\d+ \w+ ago')
        list_of_date_posts.extend(
            response.xpath(
                '//div[contains(@class,"container")]'
                '/div[contains(@class,"news-feed")]'
                '/section[contains(@class,"list-feed")]'
                '/div[contains(@class,"posts clearfix")]'
                '/div[contains(@class,"list-post clearfix")]'
                '/article/div[contains(@class,"content")]'
                '/div[contains(@class,"title")]'
                '/span[contains(@class,"post-meta")]/text()'
            ).re(r'\d+ \w+ ago')
        )
        list_of_posts_links.extend(
            response.xpath(
                '//div[contains(@class,"container")]'
                '/div[contains(@class,"news-feed")]'
                '/section[contains(@class,"list-feed")]'
                '/div[contains(@class,"posts clearfix")]'
                '/div/article/a/@href'
            ).getall())

        news_item = CryptoSlateItem()
        news_item['name_of_group'] = response.xpath(
            '//div[contains(@class,"container")]'
            '/div[contains(@class,"news-feed")]'
            '/div[contains(@class,"widget-title")]'
            '/h3/text()'
        ).re(" .* ")[0].strip()

        for counter in range(0, len(list_of_posts_links)-1):
            self.date_filter(
                self.days_ago_to_date(list_of_date_posts[counter]))
            yield response.follow(list_of_posts_links[counter],
                                  self.parse_news,
                                  meta={'news_item': news_item}
                                  )
        if response.xpath(
                '//div[contains(@class,"site-navigation clearfix")]/a/@href'):
            scrapy.Request(
                response.xpath(
                    '//div[contains(@class,"site-navigation clearfix")]'
                    '/a/@href'
                ).get(),
                self.parse_list_of_links_news,)

    def parse_news(self, response):
        news_item = response.meta['news_item']
        news_item['main_url'] = self.start_urls[0]
        news_item['name_of_subgroup'] = response.xpath(
            '//div[contains(@class,"title clearfix ")]'
            '/span[contains(@class, "post-category")]/span/a/text()'
        ).get()
        news_item['title'] = response.xpath(
            '//div[contains(@class,"post-container")]'
            '/div[contains(@class,"post")]/@data-title'
        ).get()

        news_item['authors'] = []
        news_item['authors'].append(
            response.xpath(
                '//div[contains(@class,"post-container")]'
                '/div[contains(@class,"post")]'
                '/div[contains(@class,"title clearfix")]'
                '/div[contains(@class,"post-meta clearfix")]'
                '/span/span[contains(@class,"post-author")]/text()'
            ).get())

        news_item['date'] = self.date_to_iso(response.xpath(
            '//span[contains(@class,"post-date")]/text()'
        ).get())
        news_item['text'] = response.xpath(
            '//div[contains(@class,"post-box clearfix")]/article'
        ).get()

        yield news_item

    def date_filter(self, date):
        if (datetime.datetime.now() - date).days > int(self.days):
            raise scrapy.exceptions.IgnoreRequest('invalid date')

    @staticmethod
    def days_ago_to_date(date):
        value, unit = re.search(r'(\d+) (\w+) ago', date.strip()).groups()
        if not unit.endswith('s'):
            unit += 's'
        if unit == 'mins':
            unit = 'minute'
        delta = relativedelta(**{unit: int(value)})
        return datetime.datetime.now() - delta

    @staticmethod
    def date_to_iso(date):
        return datetime.datetime.strptime(
            date, '%B %d, %Y at %I:%M %p %Z').isoformat()
