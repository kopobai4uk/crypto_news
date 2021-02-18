import scrapy
from crypto_news.items import DailyCoinNewsItem
from scrapy import FormRequest, exceptions
import datetime

const_form_data = {
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
    start_urls = ['https://dailycoin.com/',]
    pagination_url = 'https://dailycoin.com/wp-admin/admin-ajax.php'

    def parse(self, response, **kwargs):
        list_of_category_crypto_news = set(response.xpath(
            '//div[@class="mkd-menu-inner"]/ul/li/a/@href').re('.*news\/$'))
        yield from response.follow_all(list_of_category_crypto_news,
                                       self.parse_list_news_links,)

    def check_date(self, list_of_dates):
        for date in list_of_dates:
            clean_date = datetime.datetime.strptime(date.strip(),
                                                    '%B %d, %Y').date()
            if (datetime.datetime.now().date() - clean_date).days > int(
                    self.days):
                raise exceptions.IgnoreRequest('data incorect')

    def parse_list_news_links(self, response):
        name_of_group = response.xpath('//h5[contains(@class,'
                                       '"mkd-title-line-head")]'
                                       '/text()').get().strip()
        list_of_news = response.xpath('//a[@class="mkd-pt-title-link"]'
                                      '/@href').getall()

        list_of_dates = response.xpath('//div[contains(@class,'
                                       ' "mkd-post-info-date'
                                       ' entry-date updated")]'
                                       '/span/text()').getall()
        self.check_date(list_of_dates)

        yield from response.follow_all(list_of_news,
                                       self.parse_news,
                                       meta={
                                           'name_of_group': name_of_group})
        form_data = const_form_data.copy()

        form_data['max_pages'] = str(
            response.xpath('//div[contains(@class,"mkd-bnl-holder'
                           ' mkd-pl-five-holder'
                           '  unique-category-template-three'
                           ' mkd-post-columns-1 mkd-post-pag-infinite")]/'
                           '@data-max_pages').get())
        form_data['category_id'] = str(
            response.xpath('//div[contains(@class, "mkd-bnl-holder'
                           ' mkd-pl-five-holder'
                           '  unique-category-template-three'
                           ' mkd-post-columns-1 mkd-post-pag-infinite")]/'
                           '@data-category_id').get())

        if int(form_data['max_pages']) > 1:
            yield FormRequest(url=self.pagination_url,
                              formdata=form_data,
                              callback=self.parse_list_news_links_ajax,
                              meta={'form_data': form_data})

    def parse_list_news_links_ajax(self, response):
        form_data = response.meta['form_data']

        if int(form_data['paged']) <= int(form_data['max_pages']):

            list_of_dates = response.xpath('//div[contains(@class,'
                                           '"mkd-post-info-date")]'
                                           '/span/text()').getall()
            list_of_news_clean = []
            for date in list_of_dates:
                if (''.join(c for c in date if c not in '\\n')).strip():
                    list_of_news_clean.append(
                        ''.join(c for c in date if c not in '\\n'))
            list_of_news_clean.pop()
            self.check_date(list_of_news_clean)

            name_of_group = response.xpath('//div[contains(@class,'
                                           '"mkd-post-info-category")]'
                                           '/a/text()').get()
            list_of_news = response.xpath('//a[contains(@class,'
                                          ' "mkd-pt-title-link")]'
                                          '/@href').getall()

            for i in range(0, len(list_of_news)):
                list_of_news[i] = list_of_news[i].replace('\\', '')
                list_of_news[i] = list_of_news[i].replace('"', '')

            yield from response.follow_all(list_of_news,
                                           self.parse_news,
                                           meta={
                                               'name_of_group': name_of_group})
            form_data['next_page'] = str(int(form_data['next_page']) + 1)
            form_data['paged'] = str(int(form_data['paged']) + 1)

            yield FormRequest(url=self.pagination_url,
                              formdata=form_data,
                              callback=self.parse_list_news_links_ajax,
                              meta={'form_data': form_data})

    def parse_news(self, response):
        news = DailyCoinNewsItem()
        news['main_url'] = self.start_urls[0]
        news['name_of_group'] = response.meta['name_of_group']
        news['title'] = response.xpath('//h1[contains(@class,'
                                       '"entry-title mkd-post-title")]/'
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
