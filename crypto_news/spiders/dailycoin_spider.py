import scrapy
from crypto_news.items import DailyCoinNewsItem
import w3lib.html


class DailyCoinSpider(scrapy.Spider):

    name = 'daily_coin_spider'
    start_urls = ['https://dailycoin.com/']

    def parse(self, response, **kwargs):
        list_of_category_crypto_news = response.xpath(
            '//div[@class="mkd-menu-inner"]/ul/li/a/@href').re('.*news\/$')
        yield from response.follow_all(list_of_category_crypto_news,
                                       self.parse_list_news_links,)

    def parse_list_news_links(self, response):
        print('777777777777')
        print(self.start_urls[0])
        print('777777777777777')
        name_of_group = response.xpath('//h5[contains(@class,'
                                       '"mkd-title-line-head")]/text()')\
            .get().strip()
        response.meta['name_of_group'] = name_of_group
        list_of_news = response.xpath('//a[@class="mkd-pt-title-link"]/@href')\
            .getall()
        yield from response.follow_all(list_of_news,
                                       self.parse_news,
                                       meta={'name_of_group': name_of_group})

    def parse_news(self, response):
        news = DailyCoinNewsItem()
        news['main_url'] = self.start_urls[0]
        news['name_of_group'] = response.meta['name_of_group']
        news['title'] = response.xpath('//h1[contains(@class,'
                                       ' "entry-title mkd-post-title")]/'
                                       'text()').get()
        news['text'] = response.xpath('//div[contains(@class, "wpb_wrapper")]'
                                      '//text()').getall()
        news['date'] = response.xpath('//div[contains(@class,'
                                      ' "mkd-post-info clearfix")]'
                                      '/div[contains(@class,'
                                      '"mkd-post-info-date '
                                      'entry-date updated")]/span/'
                                      'text()').get().strip()
        news['author'] = response.xpath('//div[contains(@class,'
                                        ' "mkd-post-info clearfix")]'
                                        '/div[contains'
                                        '(@class, "post-info-author")]/'
                                        'span/text()').get().strip()
        yield news
