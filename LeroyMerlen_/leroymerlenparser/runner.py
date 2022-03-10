# Глобальные модули
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

# Локальные модули
from leroymerlenparser import settings
from leroymerlenparser.spiders.lmerlenru import LmerlenruSpider

search = 'plastikovye-okna'

# Создаем стандартную точку входа
if __name__ == '__main__':
    crawler_settings = Settings()  # создаем настройки
    crawler_settings.setmodule(settings)  # создаем объект с настройками

    process = CrawlerProcess(settings=crawler_settings)  # создаем процесс с настройками

    process.crawl(LmerlenruSpider, search=search)  # определение рабочего паука

    process.start()  # запуск процесса
