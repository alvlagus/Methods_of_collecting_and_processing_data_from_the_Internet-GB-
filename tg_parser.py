from telethon import TelegramClient
import time
import app_config
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke

# Подгружаем данные для входа из вспомогательного файла
api_id = app_config.api_id
api_hash = app_config.api_hash

#  Подключение базы данных MongoDB
DB_client = MongoClient('localhost', 27017)

db = DB_client['Telegram']  # database
tg_members = db.members  # collection for members
tg_msg = db.msg  # collection for messages

# # Очистка коллекции БД:
# tg_members.delete_many({})
# tg_msg.delete_many({})

client = TelegramClient('tg_reg', api_id, api_hash)

async def main():
    dialogs = await client.get_dialogs()
    for dialog in dialogs:
        if dialog.title == 'Phoenix Media Chat':
            members = await client.get_participants(dialog)  # работает для чатов, но не работает для каналов
            for member in members:
                members_list = {
                    'username': member.username,
                    'user_id': member.id,
                    'phone': member.phone,
                    'first_name': member.first_name,
                    'last_name': member.last_name
                }

                #  Запись members_list в БД:
                try:
                    tg_members.update_one(members_list, {'$set': members_list}, upsert=True)
                except dke:
                    print('Duplicate key error collection')
                time.sleep(0.5)

            async for msg in client.iter_messages(dialog):
                msg_list = {
                    'date': msg.date,
                    'sender_id': msg.sender_id,
                    'username': msg.sender.username,
                    'first_name': msg.sender.first_name,
                    'last_name': msg.sender.last_name,
                    'text': msg.text
                }
                time.sleep(1)

                #  Запись msg_list в БД:
                try:
                    tg_msg.update_one(msg_list, {'$set': msg_list}, upsert=True)
                except dke:
                    print('Duplicate key error collection')
    pass

with client:
    client.loop.run_until_complete(main())
