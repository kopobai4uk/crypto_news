import scrapy
from w3lib.html import remove_tags
from itemloaders.processors import Join, MapCompose, TakeFirst


class CryptoSlateItem(scrapy.Item):
    main_url = scrapy.Field(input_processor=MapCompose(remove_tags),
                            output_processor=Join(),)
    name_of_group = scrapy.Field(input_processor=MapCompose(remove_tags),
                                 output_processor=Join(),)
    name_of_subgroup = scrapy.Field(input_processor=MapCompose(remove_tags),
                                    output_processor=Join(),)
    title = scrapy.Field(input_processor=MapCompose(remove_tags),
                         output_processor=Join(),)
    authors = scrapy.Field(input_processor=MapCompose(remove_tags),
                           output_processor=Join(),)
    date = scrapy.Field(input_processor=MapCompose(remove_tags),
                        output_processor=Join(),)
    text = scrapy.Field(input_processor=MapCompose(remove_tags),
                        output_processor=Join(),)