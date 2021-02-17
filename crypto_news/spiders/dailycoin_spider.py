import scrapy
from crypto_news.items import DailyCoinNewsItem
import w3lib.html
from scrapy import FormRequest
import pdb

const_formdata = {
        'next_page': None,
        'max_pages': None,
        'paged': None,
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
    start_urls = ['https://dailycoin.com/',]
    pagination_url = 'https://dailycoin.com/wp-admin/admin-ajax.php'

    page_inch = 2



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


        formdata = const_formdata.copy()
        print(formdata)

        formdata['next_page'] = str(self.page_inch)
        formdata['paged'] = str(self.page_inch)
        formdata['max_pages'] = str(
            response.xpath('//div[contains(@class,'
                                             '"mkd-bnl-holder'
                                             ' mkd-pl-five-holder'
                                             '  unique-category-template-three'
                                             ' mkd-post-columns-1'
                                             ' mkd-post-pag-infinite")]/'
                                             '@data-max_pages').get())
        formdata['category_id'] = str(
            response.xpath('//div[contains(@class,'
                                               ' "mkd-bnl-holder'
                                               ' mkd-pl-five-holder'
                                               '  unique-category-template-three'
                                               ' mkd-post-columns-1'
                                               ' mkd-post-pag-infinite")]/'
                                               '@data-category_id').get())
        # pdb.set_trace()

        if int(formdata['max_pages']) > 1:
            yield FormRequest(url=self.pagination_url, formdata=formdata,
                              callback=self.parse_list_news_links_ajax,
                              meta={'formdata': formdata})
            print('after')

    def parse_list_news_links_ajax(self, response):

        formdata = response.meta['formdata']
        # pdb.set_trace()
        print(formdata)
        # print('this is fuc {}-page_inch  {}-data_max_pages'.format(
        #     self.page_inch, self.formdata['max_pages']))
        self.page_inch += 1

        if int(self.page_inch) <= int(formdata['max_pages']):
            name_of_group = response.xpath('//div[contains(@class,'
                                           '"mkd-post-info-category")]'
                                           '/a/text()').get()
            list_of_news = response.xpath(
                '//a[contains(@class, "mkd-pt-title-link")]/@href').getall()
            # pdb.set_trace()
            for i in range(0, len(list_of_news)):
                list_of_news[i] = list_of_news[i].replace('\\', '')
                list_of_news[i] = list_of_news[i].replace('"', '')
            yield from response.follow_all(list_of_news,
                                           self.parse_news,
                                           meta={
                                               'name_of_group': name_of_group})
            formdata['next_page'] = str(self.page_inch)
            formdata['paged'] = str(self.page_inch)
            print(formdata)
            # pdb.set_trace()

            yield FormRequest(url=self.pagination_url, formdata=formdata,
                              callback=self.parse_list_news_links_ajax,
                              meta={'formdata':formdata})

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
