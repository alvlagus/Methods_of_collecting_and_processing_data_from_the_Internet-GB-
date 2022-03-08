# Глобальные модули
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

# Локальные модули
from jobparser import settings
from jobparser.spiders.hhru import HhruSpider
from jobparser.spiders.sjru import SjruSpider

# Создаем стандартную точку входа
if __name__ == '__main__':
    crawler_settings = Settings()  # создаем настройки
    crawler_settings.setmodule(settings)  # создаем объект с настройками

    process = CrawlerProcess(settings=crawler_settings)  # создаем процесс с настройками
    process.crawl(HhruSpider)  # определение рабочего паука
    process.crawl(SjruSpider)  # определение рабочего паука

    process.start()  # запуск процесса
