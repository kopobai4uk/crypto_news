import scrapy
import lxml.html
import datetime
from crypto_news.items import CryptoNewsItem
import demjson

const_form_data = {
    "event": "articles.articles#morepages",
    "where": None,
    "offset": "48",
    "articles_type": "1"
}


class CryptoNewsSpider(scrapy.Spider):

    name = 'crypto_news'
    start_urls = ['https://cryptonews.com/',]

    def parse(self, response):
        list_of_category_links = response.xpath('//div[contains(@class, "cn-sub-nav")]'
                                                '/a/@href').re('^\/news.*')
        yield from response.follow_all(list_of_category_links,
                                       self.parse_list_of_news)

    def parse_list_of_news(self, response):
        links_of_news_links = response.xpath('//div[contains(@class,'
                                             '"cn-tile article")]'
                                             '/a/@href').getall()
        list_of_date_posted_news = response.xpath('//div[contains(@class,"cn-tile article")]'
                                                  '/div[contains(@class,"props")]'
                                                  '/span[contains(@class,"notch")]'
                                                  '/i/time/@datetime').getall()
        if response.xpath('//script/text()').re(".*_load_more.*"):
            script_function = response.xpath('//script/text()').re(".*_load_more.*")[0]
            js_dict = demjson.decode(script_function[20:])
            formatted_data_form_script = lxml.html.fromstring(js_dict['pages'][0])
            links_of_news_links.extend(
                formatted_data_form_script.xpath('//div/a/@href'))
            list_of_date_posted_news.extend(
                formatted_data_form_script.xpath('//time/@datetime'))

        for counter in range(0, len(links_of_news_links)-1):
            self.data_filter(list_of_date_posted_news[counter])
            yield scrapy.Request(self.start_urls[0][:-1]
                                 + links_of_news_links[counter], self.parse_news)

        if response.xpath('//div[contains(@class, "cn-section-controls")]'):
            form_data = const_form_data.copy()
            form_data['where'] = js_dict['where']
            yield scrapy.FormRequest(url=response.url,
                                     formdata=form_data,
                                     callback=self.parse_list_of_news_load_more,
                                     meta={'form_data': form_data})

    def parse_list_of_news_load_more(self, response):
        form_data = response.meta('form_data')
        form_data['offset'] = str(response['offset'])
        for page in response['pages']:
            formatted_page = lxml.html.fromstring(page)
            list_of_news_links = formatted_page.xpath('//div/a/@href')
            list_of_dates_links = formatted_page.xpath('//time/@datetime')
            for counter in range(0, len(list_of_news_links)-1):
                self.data_filter(list_of_dates_links[counter])
                yield scrapy.Request(self.start_urls[0][:-1]
                                     + list_of_news_links[counter],
                                     self.parse_news)

    def data_filter(self, date):
        if (datetime.datetime.now() - datetime.datetime.fromisoformat(date)
                .replace(tzinfo=None)).days > int(self.days):
            raise scrapy.exceptions.IgnoreRequest('data incorrect')

    def parse_news(self, response):
        news_item = CryptoNewsItem()
        news_item['main_url'] = self.start_urls[0]
        news_item['name_of_group'] = response.xpath('//div[contains(@class,'
                                                    '"cn-tree padded")]/a/'
                                                    'text()').getall()[-1]
        news_item['title'] = response.xpath('//article[contains(@class,'
                                            '"cn-article-page")]/h1/text()').get()
        news_item['author'] = []
        if response.xpath('//div[contains(@class,"cn-props-panel")]'
                          '/div[contains(@class,"author")]/span/text()').get():
            news_item['author'].append(
                response.xpath('//div[contains(@class,"cn-props-panel")]'
                               '/div[contains(@class,"author")]'
                               '/span/text()').get())
        else:
            news_item['author'].append(
                response.xpath('//div[contains(@class,"cn-props-panel")]'
                               '/div[contains(@class,"author")]'
                               '/span/a/text()').get())

        news_item['date'] = response.xpath('//div[contains(@class,"cn-props-panel")]'
                                           '/div[contains(@class,"time")]'
                                           '/time/@datetime').get()

        news_item['text'] = response.xpath('//div[contains(@class,"cn-content")]'
                                           '/p/text()').getall()

        yield news_item
