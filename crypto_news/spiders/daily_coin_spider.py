import scrapy
from crypto_news.items import DailyCoinNewsItem
from scrapy import FormRequest, exceptions
from scrapy.loader import ItemLoader
import datetime
import re

FORM_DATA = {
        'next_page': str(2),
        'max_pages': None,
        'paged': str(2),
        'pagination_type': 'infinite',
        'display_pagination': 'yes',
        'excerpt_length': '24',
        'display_excerpt': 'yes',
        'display_author': 'yes',
        'category_id': None,
        'column_number': '1',
        'number_of_posts': '4',
        'extra_class_name': 'unique-category-template-three',
        'base': 'mkd_post_layout_five',
        'action': 'newshub_mikado_list_ajax',
}


class DailyCoinSpider(scrapy.Spider):

    name = 'daily_coin_spider'
    start_urls = ['https://dailycoin.com/', ]
    pagination_url = 'https://dailycoin.com/wp-admin/admin-ajax.php'

    def parse(self, response, **kwargs):
        list_of_category_crypto_news = set(response.xpath(
            '//div[@class="mkd-menu-inner"]/ul/li/a/@href').re('.*news\/$'))
        yield from response.follow_all(list_of_category_crypto_news,
                                       self.parse_list_news_links,)

    def parse_list_news_links(self, response):
        list_of_news_links = response.xpath(
            '//a[@class="mkd-pt-title-link"]/@href'
        ).getall()
        list_of_dates = response.xpath(
            '//div[contains(@class, "mkd-post-info-date entry-date updated")]'
            '/span/text()'
        ).getall()
        for counter in range(0, len(list_of_news_links)-1):
            self.check_date(list_of_dates[counter])
            news_item = ItemLoader(DailyCoinNewsItem(), response=response)
            name_of_group = response.xpath(
                '(//div[contains(@class, "mkd-post-info-category")])[1]'
                '/a/text()'
            ).get()
            news_item.add_value(
                'name_of_group',
                self.clean_category_date(name_of_group)
            )
            yield scrapy.Request(list_of_news_links[counter],
                                 self.parse_news,
                                 meta={'news_item': news_item.load_item()}
                                 )
        form_data = FORM_DATA.copy()
        form_data['max_pages'] = str(
            response.xpath(
                '//div[contains(@class,"mkd-bnl-holder mkd-pl-five-holder'
                '  unique-category-template-three mkd-post-columns-1'
                ' mkd-post-pag-infinite")]/@data-max_pages'
            ).get())
        form_data['category_id'] = str(
            response.xpath(
                '//div[contains(@class, "mkd-bnl-holder mkd-pl-five-holder'
                '  unique-category-template-three mkd-post-columns-1'
                ' mkd-post-pag-infinite")]/@data-category_id'
            ).get())
        if int(form_data['max_pages']) > 1:
            yield FormRequest(url=self.pagination_url,
                              formdata=form_data,
                              callback=self.parse_list_news_links_ajax,
                              meta={'form_data': form_data})

    def parse_list_news_links_ajax(self, response):
        form_data = response.meta['form_data']

        if int(form_data['paged']) <= int(form_data['max_pages']):

            list_of_dates = response.xpath(
                '//div[contains(@class, "mkd-post-info-date")]'
                '/span/text()'
            ).getall()
            list_of_news = response.xpath(
                '//a[contains(@class, "mkd-pt-title-link")]/@href'
            ).getall()
            list_of_news_date_clean = []
            for date in list_of_dates:
                if (''.join(c for c in date if c not in '\\n')).strip():
                    list_of_news_date_clean.append(
                        ''.join(c for c in date if c not in '\\n'))
            list_of_news_date_clean.pop()

            for counter in range(0, len(list_of_news)-1):
                self.check_date(list_of_news_date_clean[counter])
                news_item = ItemLoader(DailyCoinNewsItem(), response=response)
                name_of_group = response.xpath(
                    '(//div[contains(@class, "mkd-post-info-category")])[1]'
                    '/a/text()'
                ).get()
                news_item.add_value(
                    'name_of_group',
                    self.clean_category_date(name_of_group)
                )
                list_of_news[counter] = list_of_news[counter].replace('\\', '')
                list_of_news[counter] = list_of_news[counter].replace('"', '')
                yield scrapy.Request(list_of_news[counter],
                                     self.parse_news,
                                     meta={'news_item': news_item.load_item()}
                                     )
            form_data['next_page'] = str(int(form_data['next_page']) + 1)
            form_data['paged'] = str(int(form_data['paged']) + 1)

            yield FormRequest(url=self.pagination_url,
                              formdata=form_data,
                              callback=self.parse_list_news_links_ajax,
                              meta={'form_data': form_data}
                              )

    def parse_news(self, response):
        news_item = ItemLoader(response.meta['news_item'], response=response)
        news_item.add_value('main_url', self.start_urls[0])
        news_item.add_xpath(
            'title',
            '//h1[contains(@class, "entry-title mkd-post-title")]/text()'
        )
        news_item.add_value(
            'date',
            self.date_to_iso(response.xpath(
                '//div[contains(@class, "mkd-post-info clearfix")]'
                '/div[contains(@class, "mkd-post-info-date'
                ' entry-date updated")]/span/text()'
            ).get())
        )
        news_item.add_xpath(
            'authors',
            '//div[contains(@class, "mkd-post-info clearfix")]'
            '/div[contains(@class, "post-info-author")]/span/text()',
            re='(?<=by ).*$'
            )
        news_item.add_xpath(
            'text',
            '//div[contains(@class, "vc_column-inner")]'
        )
        yield news_item.load_item()

    @staticmethod
    def date_to_iso(date):
        return datetime.datetime.strptime(date.strip(),
                                          '%B %d, %Y').isoformat()

    def check_date(self, date):
        if ((datetime.datetime.now()
             - datetime.datetime.strptime(date.strip(),
                                          '%B %d, %Y')
        ).days) > int(self.days):
            raise exceptions.IgnoreRequest('incorrect date')

    @staticmethod
    def clean_category_date(category):
        res = ''
        for item in re.findall(r'(\w+).(\w+)', category)[0]:
            res = res + item + ' '
        return res.strip()



