import scrapy
from crypto_news.items import CoinTelegraphNews


class CointelegraphNewsSpider(scrapy.Spider):
    name = 'Cointelegraph_News'
    allowed_domains = ['https://cointelegraph.com/']
    start_urls = ['https://cointelegraph.com//']

    def parse(self, response, **kwargs):
        category_list = response.css(
            "li.menu-desktop__item div.menu-desktop-sub__list-wrp a::attr(href)").re(r'tags/\w+')
        print(category_list)
        yield from response.follow_all(category_list, self.parse_list_news)

    # def parse(self, response, **kwargs):
    #     tmp = response.css("li.menu-desktop__item div.menu-desktop-sub__list-wrp a::attr(href)").re(r'tags/\w+')
    #     for href in tmp:
    #         yield response.follow(response.urljoin(href), self.parse_list_news)

    def parse_list_news(self, response):
        list_of_news= response.css(
            "div.tag-page ul.posts-listing__list a.post-card-inline__figure-link::attr(href)").get()
        print(list_of_news)
        yield from response.follow_all(list_of_news, self.parse_news)

    # def parse_list_news(self, response):
    #     tmp = response.css(
    #             "div.tag-page ul.posts-listing__list a.post-card-inline__figure-link::attr(href)").getall()
    #     for href in tmp:
    #         yield scrapy.Request(response.urljoin(self.start_urls[0], href), self.parse_news)

    def parse_news(self, response):
        news = CoinTelegraphNews()
        news['title'] = response.css("")
        news['text'] = response.css("").getall()
        news['date'] = response.css("")
        news['author'] = response.css("")

        yield news
