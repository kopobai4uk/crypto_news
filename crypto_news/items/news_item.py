import scrapy


class NewsItem(scrapy.Item):
    main_url = scrapy.Field()
    name_of_group = scrapy.Field()
    title = scrapy.Field()
    authors = scrapy.Field()
    date = scrapy.Field()
    text = scrapy.Field()
