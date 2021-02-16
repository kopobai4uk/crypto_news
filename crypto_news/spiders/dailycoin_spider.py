import scrapy
from crypto_news.items import DailyCoinNewsItem
import w3lib.html
from scrapy import FormRequest


class DailyCoinSpider(scrapy.Spider):

    name = 'daily_coin_spider'
    start_urls = ['https://dailycoin.com/',]
    pagination_url = 'https://dailycoin.com/wp-admin/admin-ajax.php'

    data_max_pages = None
    data_category_id = None
    page_inch = 1

    def parse(self, response, **kwargs):
        list_of_category_crypto_news = response.xpath(
            '//div[@class="mkd-menu-inner"]/ul/li/a/@href').re('.*news\/$')
        yield from response.follow_all(list_of_category_crypto_news,
                                       self.parse_list_news_links,)

    def parse_list_news_links(self, response):

        name_of_group = response.xpath('//h5[contains(@class,'
                                       ' "mkd-title-line-head")]/text()')\
            .get().strip()
        list_of_news = response.xpath(
            '//a[@class="mkd-pt-title-link"]/@href') \
            .getall()
        yield from response.follow_all(list_of_news,
                                       self.parse_news,
                                       meta={
                                           'name_of_group': name_of_group})
        self.data_max_pages = response.xpath('//div[contains(@class,'
                                             '"mkd-bnl-holder'
                                             ' mkd-pl-five-holder'
                                             '  unique-category-template-three'
                                             ' mkd-post-columns-1'
                                             ' mkd-post-pag-infinite")]/'
                                             '@data-max_pages').get()
        self.data_category_id = response.xpath('//div[contains(@class,'
                                               ' "mkd-bnl-holder'
                                               ' mkd-pl-five-holder'
                                               '  unique-category-template-three'
                                               ' mkd-post-columns-1'
                                               ' mkd-post-pag-infinite")]/'
                                               '@data-category_id').get()
        print(self.data_max_pages)
        if int(self.data_max_pages) > 1:
            print('befor')
            self.parse_list_news_links_ajax(response)
            print('after')

    def parse_list_news_links_ajax(self, response):
        self.page_inch += 1
        if self.page_inch <= self.data_max_pages:
            formdata = {
                'next_page': str(self.page_inch),
                'max_pages': self.data_max_pages,
                'paged': str(self.page_inch),
                'pagination_type': 'infinite',
                'display_pagination': 'yes',
                'excerpt_length': '24',
                'display_excerpt': 'yes',
                'display_author': 'yes',
                'category_id': self.data_category_id,
                'column_number': '1',
                'number_of_posts': '4',
                'extra_class_name': 'unique-category-template-three',
                'base': 'mkd_post_layout_five',
                'action': 'newshub_mikado_list_ajax',
            }
            name_of_group = response.xpath('//div[contains(@class,'
                                           '"mkd-post-info-category")]'
                                           '/a/text()').get()
            list_of_news = response.xpath(
                '//a[contains(@class, "mkd-pt-title-link")]/@href').getall()
            for i in range(0, len(list_of_news)):
                list_of_news[i] = list_of_news[i].replace('\\', '')
                list_of_news[i] = list_of_news[i].replace('"', '')
            yield from response.follow_all(list_of_news,
                                           self.parse_news,
                                           meta={
                                               'name_of_group': name_of_group})

            yield FormRequest(url=self.pagination_url, formdata=formdata,
                              callback=self.parse_list_news_links_ajax)
        else:
            return

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
