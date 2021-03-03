import scrapy
from scrapy.loader import ItemLoader
import demjson
import datetime
import lxml.html
from scrapy import exceptions
from dateutil.relativedelta import relativedelta
import re
from crypto_news.items import NewsBtcItem

FORM_DATA = {
    "lang": "en_US",
    "action": "jnews_module_ajax_jnews_block_3",
    "module": "true",
    "data[filter]": "0",
    "data[filter_type]": "all",
    "data[current_page]": "2",
}


class NewsBtcSpider(scrapy.Spider):

    name = 'news_bts_spider'
    start_urls = ['https://www.newsbtc.com/']
    pagination_url = 'https://www.newsbtc.com/?ajax-request=jnews'

    def parse(self, response, **kwargs):
        list_of_category = response.xpath(
            '//div[contains(@class, "jeg_nav_item")]'
            '/ul[contains(@class,"jeg_menu jeg_main_menu")]'
            '/li[contains(@id,"menu-item-319416")]/ul/li/a/@href'
        )
        yield from response.follow_all(list_of_category,
                                       self.parse_list_of_news_links)

    def parse_list_of_news_links(self, response):
        if response.xpath('//div[contains(@class, "jeg_empty_module")]'):
            return
        list_of_main_post_links = response.xpath(
            '//div[contains(@class, "jeg_heroblock_wrapper")]'
            '/article/div/div[contains(@class, "jeg_postblock_content")]'
            '/div[contains(@class, "jeg_post_info")]'
            '/div[contains(@class, "jeg_post_meta")]/div/a/@href'
        ).getall()
        list_of_main_post_date = response.xpath(
            '//div[contains(@class, "jeg_heroblock_wrapper")]'
            '/article/div/div[contains(@class, "jeg_postblock_content")]'
            '/div[contains(@class, "jeg_post_info")]'
            '/div[contains(@class, "jeg_post_meta")]/div/a/text()'
        ).getall()

        if list_of_main_post_links:
            for counter in range(0, len(list_of_main_post_links)-1):
                self.date_filter(
                    self.days_ago_to_date(list_of_main_post_date[counter])
                )
                yield scrapy.Request(list_of_main_post_links[counter],
                                     self.parse_news)

        list_of_post_links = response.xpath(
            '//div[contains(@class,"jeg_posts jeg_load_more_flag")]'
            '/article[contains(@class,"jeg_post jeg_pl_md_2")]'
            '/div[contains(@class, "jeg_thumb")]/a/@href'
        ).getall()
        list_of_post_dates = response.xpath(
            '//div[contains(@class,"jeg_posts jeg_load_more_flag")]'
            '/article[contains(@class,"jeg_post jeg_pl_md_2")]'
            '/div[contains(@class, "jeg_postblock_content")]'
            '/div[contains(@class, "jeg_post_meta")]'
            '/div[contains(@class, "jeg_meta_date")]/a/text()'
        ).getall()
        if list_of_post_links:
            for counter in range(0, len(list_of_post_links)-1):
                self.date_filter(self.days_ago_to_date(
                    list_of_post_dates[counter]))
                yield scrapy.Request(list_of_post_links[counter],
                                     self.parse_news)

        if response.url == 'https://www.newsbtc.com/press-releases/':
            next_page = response.xpath(
                '//div[contains(@class,"jeg_navigation jeg_pagination")]'
                '/a[contains(@class,"page_nav next")]/@href'
            ).get()
            if next_page:
                yield scrapy.Request(next_page, self.parse_list_of_news_links)
        if response.xpath(
                '//div[contains(@class,"jeg_block_navigation")]'
                '/div[contains(@class, "jeg_block_loadmore")]'
                '/a/@class').get() != 'disabled' \
                and response.url != 'https://www.newsbtc.com/press-releases/':
            scrip_with_clean_data = demjson.decode(response.xpath(
                '//div[contains(@class,"jnews_category_content_wrapper")]'
                '/div/script/text()'
            ).get()[42:-1])
            form_data = FORM_DATA.copy()
            for key, value in scrip_with_clean_data.items():
                if value is True:
                    form_data["data[attribute][" + key + "]"] \
                        = 'true'
                elif value is False:
                    form_data["data[attribute][" + key + "]"] \
                        = 'false'
                else:
                    form_data["data[attribute][" + key + "]"] \
                        = value
                yield scrapy.FormRequest(url=self.pagination_url,
                                         formdata=form_data,
                                         callback=self.parse_pagination,
                                         meta={'form_data': form_data}
                                         )

    def parse_pagination(self, response):
        html_data = lxml.html.fromstring(response.json()['content'])
        list_of_post_links = html_data.xpath(
            '//article[contains(@class,"jeg_post '
            'jeg_pl_md_2 format-standard")]'
            '/div[contains(@class, "jeg_thumb")]/a/@href')
        list_of_post_dates = html_data.xpath(
            '//article[contains(@class,"jeg_post '
            'jeg_pl_md_2 format-standard")]'
            '/div[contains(@class, "jeg_postblock_content")]'
            '/div[contains(@class, "jeg_post_meta")]'
            '/div[contains(@class, "jeg_meta_date")]/a/text()'
        )
        for counter in range(0, len(list_of_post_links)-1):
            self.date_filter(self.days_ago_to_date(
                list_of_post_dates[counter]))
            yield scrapy.Request(list_of_post_links[counter],
                                 self.parse_news)
        if response.json()['next'] == 'true':
            form_data = response.meta['form_data']
            form_data["data[current_page]"] = \
                str(int(form_data["data[current_page]"])+1)
            yield scrapy.FormRequest(url=self.pagination_url,
                                     formdata=form_data,
                                     callback=self.parse_pagination,
                                     meta={'form_data': form_data}
                                     )

    def parse_news(self, response):
        news_item = ItemLoader(NewsBtcItem(), response=response)
        news_item.add_value('main_url', self.start_urls[0])
        news_item.add_xpath(
            'name_of_group',
            '(//div[contains(@id,"breadcrumbs")])[1]'
            '/span[contains(@class,"breadcrumb_last_link")]/a/text()'
        )
        try:
            news_item._local_values['name_of_group']
        except KeyError:
            news_item.add_value('name_of_group',
                                'Press Releases')
        news_item.add_xpath(
            'title',
            '//div[contains(@class,"entry-header")]'
            '/h1[contains(@class,"jeg_post_title")]/text()'
        )
        news_item.add_xpath(
            'authors',
            '//div[contains(@class,"jeg_meta_container")]'
            '/div/div/div[contains(@class,"jeg_meta_author")]/a/text()'
        )
        news_item.add_value(
            'date',
            self.days_ago_to_date(
                response.xpath(
                    '(//div[contains(@class,"jeg_meta_container")])[1]'
                    '/div/div/div[contains(@class,"jeg_meta_date")]/a/text()'
                ).get())
        )
        news_item.add_xpath(
            'text',
            '(//div[contains(@class, "entry-content")])[1]'
            '/div[contains(@class,"content-inner")]'
        )
        yield news_item.load_item()

    @staticmethod
    def days_ago_to_date(date):
        try:
            return datetime.datetime.strptime(date.strip(),
                                              '%B %d, %Y'
                                              ).isoformat()
        except ValueError:
            value, unit = re.search(r'(\d+) (\w+) ago', date).groups()
            if not unit.endswith('s'):
                unit += 's'
            if unit == 'mins':
                unit = 'minute'
            delta = relativedelta(**{unit: int(value)})
            return (datetime.datetime.now() - delta).isoformat()

    def date_filter(self, date):
        if (datetime.datetime.now()
            - datetime.datetime.fromisoformat(date)).days > int(self.days):
            raise scrapy.exceptions.IgnoreRequest('invalid date')
