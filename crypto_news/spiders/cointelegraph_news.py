import scrapy
from scrapy.exceptions import IgnoreRequest
from crypto_news.items import CoinTelegraphNews
from datetime import datetime, timedelta

const_form_data = {

}


class CointelegraphNewsSpider(scrapy.Spider):
    name = 'Cointelegraph_News'
    start_urls = ['https://cointelegraph.com//']
    infinite_scroll_url = ['https://conpletus.cointelegraph.com/v1/']

    def parse(self, response, **kwargs):
        category_list = response.css(
            "li.menu-desktop__item div.menu-desktop-sub__list-wrp a::attr(href)").re(r'tags/\w+')
        yield from response.follow_all(category_list,
                                       self.parse_list_news_links, )

    def parse_list_news_links(self, response):
        name_of_group = str(response).split('/')[-1]
        name_of_group = name_of_group[:-1]
        list_of_news = response.css(
            "div.tag-page ul.posts-listing__list a.post-card-inline__figure-link::attr(href)").getall()
        yield from response.follow_all(list_of_news,
                                       self.parse_news,
                                       meta={'name_of_group': name_of_group})




    def parse_news(self, response):
        news = CoinTelegraphNews()
        news['main_url'] = self.start_urls[0]
        news['name_of_group'] = response.meta['name_of_group']
        news['title'] = response.css("div.post article.post__article h1.post__title::text").get()
        news['text'] = response.css("div.post article.post__article div.post-content").getall()
        news['date'] = response.css("div.post article.post__article time::attr(datetime)").get()
        news['author'] = response.css("div.post article.post__article div.post-meta__author-name::text").get()
        tmp = datetime.strptime(news['date'], '%Y-%m-%d')
        if datetime.today() - tmp > timedelta(30):
            raise IgnoreRequest('all new in this date range parsed')

        yield news
