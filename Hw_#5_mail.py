# загрузка библиотек
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from account import login, password
import time
from pymongo import MongoClient


#  Подключение базы данных MongoDB
client = MongoClient('localhost', 27017)
db = client['db_mail_letters']  # database
mail_letters = db.mail_letters  # collection name

# #  Очистка коллекции БД:
# yandex.delete_many({})

# импорт личных данных
LOGIN = login
PASSWORD = password

# подключение драйвера
chrome_options = Options()
chrome_options.add_argument("start-maximized")

driver = webdriver.Chrome(executable_path='./chromedriver', options=chrome_options)
driver.implicitly_wait(10)  # Задержка, неявное ожидание. Без неё не работает. Попробовать через WDW

# точка входа
driver.get('https://account.mail.ru/login/')

# вход в почту mail.ru
element = driver.find_element_by_name('username')
element.send_keys(LOGIN)
element.send_keys(Keys.ENTER)

element = driver.find_element_by_name('password')
element.send_keys(PASSWORD)
element.send_keys(Keys.ENTER)


# сбор ссылок со страницы почты
mails = {}
no_mails = False
letters_class_name = 'js-letter-list-item'

while not no_mails:
    mails_box = driver.find_elements_by_xpath(f'//a[contains(@class, "{letters_class_name}")]')
    number_of_mails = len(mails)
    for mail in mails_box:
        mail_url = mail.get_attribute('href')
        mails[mail_url] = {}
    if len(mails) == number_of_mails:
        no_mails = True
    mails_box[len(mails_box)//2].send_keys(Keys.PAGE_DOWN)
    time.sleep(0.5)

# сбор данных из ссылок
for url in mails.keys():
    elem = {}
    driver.get(url)
    elem['author'] = driver.find_element(By.XPATH, "//span[@class='letter-contact']").get_attribute('title')
    elem['data'] = driver.find_element(By.XPATH, "//div[@class='letter__date']").text
    elem['title'] = driver.find_element(By.XPATH, "//h2[@class]").text
    elem['body'] = driver.find_element(By.XPATH, "//div[contains(@class, 'body-content')]").text
    mail_letters.insert_one(elem)
    driver.back()

print(f'Collection "{mail_letters.name}" has {mail_letters.count_documents({})} letters')
# Collection "mail_letters" has 247 letters

driver.close()
