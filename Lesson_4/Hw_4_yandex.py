from pprint import pprint
import requests
from lxml import html
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke

# ◦ название источника;
# ◦ наименование новости;
# ◦ ссылку на новость;
# ◦ дата публикации.

#  Подключение базы данных MongoDB
client = MongoClient('localhost', 27017)

db = client['news']  # database
yandex = db.yandex  # collection

# #  Очистка коллекции БД:
# yandex.delete_many({})

url = 'https://yandex.ru/news'
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 '
                         'Safari/537.36'}

res = requests.get(url, headers=headers)
dom = html.fromstring(res.text)

topnews = dom.xpath("//a[contains(@href,'rubric=index&fan') and @class='mg-card__link']/ancestor::div[contains("
                    "@class,'mg-grid__item')] ")

for item in topnews:

    source = item.xpath('.//a[@class="mg-card__source-link"]/text()')
    title = item.xpath('.//h2[@class="mg-card__title"]//text()')[0].replace('\xa0', ' ')
    link = item.xpath('.//a[@href]//@href')[0]
    data = item.xpath('.//span[@class="mg-card-source__time"]/text()')

    news_list = {
        'Источник': source,
        'Название': title,
        'Ссылка': link,
        'Дата': data,
    }

    #  Запись документов в БД:
    try:
        yandex.update_one(news_list, {'$set': news_list}, upsert=True)
    except dke:
        print('Duplicate key error collection')


# pprint(news_list)

#  Просмотр результата:
for doc in yandex.find({}):
    pprint(doc)
print('Documents in collection: ', db.yandex.count_documents({}))  # Выводим количество документов в БД
