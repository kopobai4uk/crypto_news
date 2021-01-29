import scrapy
from ..items import DailyCoinNews
import w3lib.html

class DailyCoinSpider(scrapy.Spider):

    name = 'daily_coin'
    start_urls = ['https://dailycoin.com/']

    def parse(self, response, **kwargs):
        list_of_category_crypto_news = response.xpath(
            '//div[@class="mkd-menu-inner"]/ul/li/a/@href').re('.*news\/$')
        yield from response.follow_all(list_of_category_crypto_news,
                                       self.parse_list_news)

    def parse_list_news(self, response):
        # name_of_group = response.xpath('//h5[contains(@class,'
        #                                '"mkd-title-line-head")]/text()').get()
        list_of_news = response.xpath('//a[@class="mkd-pt-title-link"]/@href')\
            .getall()
        print(list_of_news)
        print("in parse_list_news")
        yield from response.follow_all(list_of_news,
                                       self.parse_news)

    def parse_news(self, response):
        news = DailyCoinNews()
        news['title'] = response.xpath('//h1[contains(@class,'
                                       ' "entry-title mkd-post-title")]/text()').get()
        text = response.xpath('//div[contains(@class, "wpb_wrapper")]//text()').getall()
        counter = 0
        for i in range(0, len(text)):
            if '\n' in text[i-counter] or '\t' in text[i-counter]:
                del text[i-counter]
                counter += 1
        news['text'] = text

        news['data'] = response.xpath('//div[contains(@class, "mkd-post-info clearfix")]/div[contains(@class,"mkd-post-info-date entry-date updated")]/span/text()').get().strip()
        news['author'] = response.xpath('//div[contains(@class,'
                                        ' "mkd-post-info clearfix")]'
                                        '/div[contains'
                                        '(@class, "post-info-author")]/'
                                        'span/text()').get().strip()

        yield news






# response.xpath('//div[contains(@class, "wpb_wrapper")]//p/text()').getall()
# b = response.xpath('//div[contains(@class, "wpb_wrapper")]')
# response.xpath('//div[contains(@class, "wpb_wrapper")]//text()').getall()
# '//div[contains(@class, "mkd-post-info clearfix")]/div[contains(@class, "mkd-post-info-date entry-date updated")]/span/text()')
