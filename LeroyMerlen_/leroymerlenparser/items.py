# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst


def get_price(price_value):
    try:
        res = int(price_value.replace(' ', ''))
        return res
    except:
        return price_value


def exchange_currency(value):
    try:
        res = value.replace('₽', 'руб.')
        return res
    except:
        return value


class LeroymerlenparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(get_price))
    price_currency = scrapy.Field(input_processor=MapCompose(exchange_currency))
    url = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    _id = scrapy.Field()
