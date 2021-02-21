import scrapy
from scrapy.exceptions import IgnoreRequest
from crypto_news.items import CoinTelegraphNews
from datetime import datetime, timedelta
import requests, json

headers = {
    'authority': 'conpletus.cointelegraph.com',
    'accept': '*/*',
    'dnt': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
    'content-type': 'application/json',
    'origin': 'https://cointelegraph.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://cointelegraph.com/tags/bitcoin',
    'accept-language': 'uk-UA,uk;q=0.9,ru;q=0.8,en-US;q=0.7,en;q=0.6',
}

json_query = {"operationName": "TagPagePostsQuery",
              "variables": {"slug": "bitcoin", "order": "postPublishedTime", "offset": 0, "length": 3, "short": "en",
                            "cacheTimeInMS": 300000},
              "query": "query TagPagePostsQuery($short: String, $slug: String!, $order: String, $offset: Int!, $length: Int!) {  locale(short: $short) {    tag(slug: $slug) {      cacheKey      id      posts(order: $order, offset: $offset, length: $length) {        data {          cacheKey          id          slug          views          postTranslate {            cacheKey          id            title           avatar           published           publishedHumanFormat          leadText            __typename        }          category {            cacheKey            id           __typename          }          author {            cacheKey            id            slug           authorTranslates {              cacheKey              id              name             __typename            }           __typename          }          postBadge {           cacheKey           id            label         postBadgeTranslates {              cacheKey              id              title             __typename            }            __typename          }          showShares          showStats          __typename        }    postsCount        __typename      }     __typename    }    __typename  }}"}


class FormRequestPaginationSpider(scrapy.Spider):
    name = "Cointelegraph_News"
    start_urls = ['https://cointelegraph.com//']
    infinite_scroll_url = 'https://conpletus.cointelegraph.com/v1/'
    news_url = 'https://cointelegraph.com/news/'

    def parse(self, response, **kwargs):
        category_list = response.css(
            "li.menu-desktop__item div.menu-desktop-sub__list-wrp a::attr(href)").re(r'tags/\w+')
        yield from response.follow_all(category_list,
                                       self.parse_list_news_category, )

    def parse_list_news_category(self, response):
        name_of_group = str(response).split('/')[-1]
        form_data = json_query
        form_data['variables']['slug'] = name_of_group[:-1]
        json_request = requests.post(url=self.infinite_scroll_url,
                                     headers=headers,
                                     data=json.dumps(form_data)
                                     )
        json_request = json_request.json()
        tmp = json_request["data"]["locale"]["tag"]["posts"]["data"]
        new_url = []
        for i in tmp:
            new_url.append(self.news_url + i["slug"])
        yield from response.follow_all(new_url,
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
