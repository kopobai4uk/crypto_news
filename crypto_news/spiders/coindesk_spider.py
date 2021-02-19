import scrapy


class CoinDeskSpider(scrapy.Spider):

    name = 'coin_desk_spider'
    start_urls = ['https://www.coindesk.com/',]

    def parse(self, response, **kwargs):
        list_of_croup_links = response.xpath('//div/div[contains(@class,'
                                             ' "submenu has-focus")]'
                                             '/ul[contains(@class,'
                                             '"submenu-list")]/li[contains'
                                             '(@class, "submenu-item")]'
                                             '/a[contains(@class,'
                                             ' "submenu-button")]/@href').getall()

        pass
