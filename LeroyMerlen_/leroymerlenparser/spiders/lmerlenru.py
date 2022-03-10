import scrapy
from scrapy.http import HtmlResponse
from leroymerlenparser.items import LeroymerlenparserItem
from scrapy.loader import ItemLoader


class LmerlenruSpider(scrapy.Spider):
    name = 'lmerlenru'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f"https://leroymerlin.ru/catalogue/{kwargs.get('search')}/"]

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[@data-qa-pagination-item="right"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//a[@data-qa='product-name']")
        for link in links:
            yield response.follow(link, callback=self.parse_ads)

    def parse_ads(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroymerlenparserItem(), response=response)
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('price_currency', "//span[@slot='currency']/text()")
        loader.add_value('url', response.url)
        loader.add_xpath('photos', "//picture[@slot='pictures']//source[contains(@media, '1024px')]/@srcset")
        yield loader.load_item()

        # name = response.xpath("//h1/text()").get()
        # price = response.xpath("//span[@slot='price']/text()").get()
        # price_currency = response.xpath("//span[@slot='currency']/text()").get()
        # url = response.url
        # photos = response.xpath("//picture[@slot='pictures']//source[contains(@media, '768px')]/@data-origin").getall()
        # yield LeroymerlenparserItem(name=name, price=price, price_currency=price_currency, url=url, photos=photos)


