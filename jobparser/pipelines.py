# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import re


class JobparserPipeline:
    def __init__(self):  # создаем БД
        client = MongoClient('localhost', 27017)
        self.mongobase = client.vacancies_0703

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            salary = item['salary']
            salary = [re.sub('\xa0', "", s) for s in salary]

            if salary[0] == 'з/п не указана':
                salary_min = None
                salary_max = None
                salary_currency = None
            elif salary[0] == 'от ':
                if salary[2] == ' до ':
                    salary_min = int(salary[1])
                    salary_max = int(salary[3])
                    salary_currency = salary[-2]
                else:
                    salary_max = None
                    salary_min = int(salary[1])
                    salary_currency = salary[-2]
            elif salary[0] == ' до':
                salary_min = None
                salary_max = int(salary[1])
                salary_currency = salary[-2]

            item['salary_min'] = salary_min
            item['salary_max'] = salary_max
            item['salary_currency'] = salary_currency
            del item['salary']

        if spider.name == 'sjru':
            salary = item['salary']
            salary = [re.sub('\xa0', "", s) for s in salary]
            salary = [re.sub('руб.', "", s) for s in salary]

            if salary[0] == 'По договорённости':
                salary_min = None
                salary_max = None
                salary_currency = None
            elif salary[0] == 'от':
                salary_min = int(salary[2])
                salary_max = None
                salary_currency = 'руб.'

            elif salary[0] == 'до':
                salary_min = None
                salary_max = int(salary[2])
                salary_currency = 'руб.'
            else:
                salary_min = int(salary[0])
                salary_max = int(salary[1])
                salary_currency = 'руб.'

            item['salary_min'] = salary_min
            item['salary_max'] = salary_max
            item['salary_currency'] = salary_currency
            del item['salary']

        collection = self.mongobase[spider.name]
        collection.insert_one(item)

        return item
