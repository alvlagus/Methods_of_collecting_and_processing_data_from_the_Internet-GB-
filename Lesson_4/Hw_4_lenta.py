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
lenta = db.lenta  # collection

# #  Очистка коллекции БД:
# lenta.delete_many({})

url = 'https://lenta.ru/'
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 '
                         'Safari/537.36'}

res = requests.get(url, headers=headers)
dom = html.fromstring(res.text)

topnews = dom.xpath("//a[contains(@class, '_topnews')]")

for item in topnews:
    source = url
    title = item.xpath('.//h3[contains(@class, "card-big__title")]//text() | .//span[contains(@class, '
                       '"card-mini__title")]//text()')
    link = item.xpath('./@href')[0]
    full_link = url + link
    data = item.xpath('.//time[contains(@class, "card-big__date")]//text() | .//time[contains(@class, '
                      '"card-mini__date")]//text()')
    news_list = {
        'Источник': url,
        'Название': title,
        'Ссылка': full_link,
        'Дата': data,
    }

    #  Запись документов в БД:
    try:
        lenta.update_one(news_list, {'$set': news_list}, upsert=True)
    except dke:
        print('Duplicate key error collection')

# pprint(news_list)

#  Просмотр результата:
for doc in lenta.find({}):
    pprint(doc)
print('Documents in collection: ', db.lenta.count_documents({}))  # Выводим количество документов в БД
