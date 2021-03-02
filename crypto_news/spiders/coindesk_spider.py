import scrapy
from urllib.parse import urlparse
import json
from scrapy import exceptions
from crypto_news.items import CoinDeskItem
import datetime


class CoinDeskSpider(scrapy.Spider):

    name = 'coin_desk_spider'
    start_urls = ['https://www.coindesk.com/',]
    pagination_url = 'https://www.coindesk.com/wp-json/v1/articles'

    def parse(self, response, **kwargs):
        list_of_groups_links = response.xpath(
            '//div'
            '/div[contains(@class,"submenu has-focus")]'
            '/ul[contains(@class,"submenu-list")]'
            '/li[contains(@class, "submenu-item")]'
            '/ul[contains(@class, "links-list list")]'
            '/li/a[contains(@class, "links-item")]'
            '/@href'
        ).re('\/tag.*')
        yield from response.follow_all(list_of_groups_links,
                                       self.parse_list_news_links
                                       )

    def parse_list_news_links(self, response):
        yield response.follow(
            self.pagination_url + urlparse(response.url).path
            + '/1?mode=list', self.parse_list_news_links_pagination
        )

    def parse_list_news_links_pagination(self, response):

        page_response_json = json.loads(
            response.body.decode('UTF-8')
        )
        for post in page_response_json['posts']:
            date = post['date']
            self.data_filter(date)
            item = CoinDeskItem()
            item['title'] = post['title']
            item['main_url'] = self.start_urls[0]
            item['name_of_group'] = post['category']['name']
            item['author'] = []
            for author in post['authors']:
                item['author'].append(author)
            item['date'] = post['date']
            slug = post['slug']
            yield scrapy.Request(self.start_urls[0]+slug,
                                 self.parse_news,
                                 meta={'item': item}
                                 )

        if page_response_json['next'] == 'null':
            raise exceptions.IgnoreRequest('Pages end')

        url = urlparse(response.url)
        yield scrapy.Request(
            self.start_urls[0][:-1] + url.path[:-1]
            + page_response_json['next'] + '/?' + url.query
        )

    def data_filter(self, date):
        if (datetime.datetime.now()
            - datetime.datetime.fromisoformat(date)).days > int(self.days):
            raise exceptions.IgnoreRequest('data incorrect')

    def parse_news(self, response):
        item = response.meta['item']
        item['text'] = response.xpath(
            '//section[contains(@class, "article-body")]'
            '/div/p/text()'
        ).getall()
        yield item
