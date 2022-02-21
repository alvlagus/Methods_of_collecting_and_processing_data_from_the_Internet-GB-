#  загружаемые библиотеки
import re
import requests
from bs4 import BeautifulSoup
from pprint import pprint
from pymongo import MongoClient
import datetime
from pycbrf.toolbox import ExchangeRates
from pymongo.errors import DuplicateKeyError as dke

#  Подключение базы данных MongoDB
client = MongoClient('localhost', 27017)

db = client['vacancy_base']  # database
hh = db.hh  # collection

# #  Очистка коллекции БД:
# hh.delete_many({})

#  Переменные
VACANCY_NAME = 'Data scientist'  # название вакансии
REQ = 400000  # Минимальная сумма для фильтрования вакансий (руб.)
base_url = 'https://hh.ru/search/vacancy'
url = 'https://hh.ru/search/vacancy'
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 '
                  'Safari/537.36'
}
params = {
    # 'search_field': 'name',
    # 'search_field': 'company_name',
    # 'search_field': 'description',
    'text': VACANCY_NAME,
    'area': 113,
    'salary': '',
    'currency_code': 'RUR',
    'experience': 'doesNotMatter',
    'order_by': 'relevance',
    'search_period': 0,
    'items_on_page': 20,
    'no_magic': 'true',
    'L_save_area': 'true',
    'page': 0,
    # 'hhtmFrom': 'vacancy_search_list'
}

# Сбор данных с сайта https://hh.ru
while True:
    response = requests.get(url, headers=headers, params=params)
    if response.ok:
        dom = BeautifulSoup(response.text, 'html.parser')
        vacancy_boxes = dom.find_all('div', {'class': 'vacancy-serp-item'})

        for vacancy_box in vacancy_boxes:
            vacancy_data = {}
            vacancy = vacancy_box.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
            vacancy_name = vacancy.getText()
            vacancy_link = vacancy.get('href')
            vacancy_address = \
                vacancy_box.find('div', {'class': 'bloko-text bloko-text_no-top-indent'}).getText().split(', ')[0]

            salary = vacancy_box.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
            if salary is None:
                salary_min = None
                salary_max = None
                salary_currency = None
            else:
                salary_str = salary.getText()
                salary_list = salary_str.split(' ')
                regex = r'[\D+\\.]?$'
                if re.search(regex, salary_str):
                    salary_currency = salary_list[-1]
                else:
                    salary_currency = None
                if salary_str.startswith('от'):
                    salary_min = int(salary_list[1].replace('\u202f', ''))
                    salary_max = None
                elif salary_str.startswith('до'):
                    salary_min = None
                    salary_max = int(salary_list[1].replace('\u202f', ''))
                else:
                    salary_min = int(salary_list[0].replace('\u202f', ''))
                    salary_max = int(salary_list[2].replace('\u202f', ''))

            #  Запись документов в словарь:
            doc = {
                'vacancy': vacancy_name,
                'city': vacancy_address,
                'salary_min': salary_min,
                'salary_max': salary_max,
                'salary_currency': salary_currency,
                'vacancy_link': vacancy_link,
                'site': 'https://hh.ru'
            }

            #  Запись документов в БД:
            try:
                hh.update_one(doc, {'$set': doc}, upsert=True)
            except dke:
                print('Duplicate key error collection')

        next_page = dom.find('a', {'data-qa': 'pager-next'})
        params['page'] += 1

    else:
        print(f'Parsing error on page {url}')
        break

#  Просмотр результата:
for doc in hh.find({}):
    pprint(doc)
print('Documents in collection: ', db.hh.count_documents({}))  # Выводим количество документов в БД

#  Данные взяты с сайта https://www.cbr.ru/.
time_now = datetime.datetime.now()
rates = ExchangeRates(time_now)
dollar = float(rates['USD'].value)
euro = float(rates['EUR'].value)


# Функция для нахождения зарплаты больше заданной
def find_salary(collection, rate: int):
    rate_rur = rate
    rate_usd = rate / dollar
    rate_eur = rate / euro
    return collection.find({'$or':
        [
            {'salary_currency': 'руб.', '$or': [{'salary_min': {'$gt': rate_rur}}, {'salary_max': {'$gt': rate_rur}}]},
            {'salary_currency': 'USD', '$or': [{'salary_min': {'$gt': rate_usd}}, {'salary_max': {'$gt': rate_usd}}]},
            {'salary_currency': 'EUR', '$or': [{'salary_min': {'$gt': rate_eur}}, {'salary_max': {'$gt': rate_eur}}]}
        ]
    })


# Вывод вакансий по условию:

res = find_salary(db.hh, rate=REQ)
for doc in res:
    pprint(doc)
