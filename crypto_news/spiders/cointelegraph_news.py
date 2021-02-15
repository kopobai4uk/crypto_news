import scrapy
from scrapy.exceptions import CloseSpider

from crypto_news.items import CoinTelegraphNews
from datetime import datetime, timedelta


class CointelegraphNewsSpider(scrapy.Spider):
    name = 'Cointelegraph_News'
    start_urls = ['https://cointelegraph.com//']

    def parse(self, response, **kwargs):
        category_list = response.css(
            "li.menu-desktop__item div.menu-desktop-sub__list-wrp a::attr(href)").re(r'tags/\w+')
        yield from response.follow_all(category_list, self.parse_list_news)

    # def parse(self, response, **kwargs):
    #     tmp = response.css("li.menu-desktop__item div.menu-desktop-sub__list-wrp a::attr(href)").re(r'tags/\w+')
    #     for href in tmp:
    #         yield response.follow(response.urljoin(href), self.parse_list_news)

    def parse_list_news(self, response):
        list_of_news = response.css(
            "div.tag-page ul.posts-listing__list a.post-card-inline__figure-link::attr(href)").getall()
        yield from response.follow_all(list_of_news, self.parse_news)

    # def parse_list_news(self, response):
    #     tmp = response.css(
    #             "div.tag-page ul.posts-listing__list a.post-card-inline__figure-link::attr(href)").getall()
    #     for href in tmp:
    #         yield scrapy.Request(response.urljoin(self.start_urls[0], href), self.parse_news)іс
    # response.css('div.post div.post-page__article div.post-meta div.post-meta__author-name').get()

    def parse_news(self, response):
        news = CoinTelegraphNews()
        news['title'] = response.css("div.post article.post__article h1.post__title::text")
        news['text'] = response.css("div.post article.post__article div.post-content").getall()
        news['date'] = datetime.strptime(response.css("div.post article.post__article time::attr(datetime)").get(),
                                     '%Y-%m-%d')
        news['author'] = response.css("div.post article.post__article div.post-meta__author-name::text").get()
        if datetime.today() - news['date'] > timedelta(6):
            raise CloseSpider('')
        yield news
