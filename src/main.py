import os
import psycopg2
from dotenv import load_dotenv

from database.create_database import create_all_tables, create_trigger, insert_test_data, create_indexes, create_procedurs

# получение данных для входа
if not load_dotenv():
    raise ValueError("Не удалось загрузить .env файл")
USER = os.getenv("USER")
PASSWD_DB = os.getenv("PASSWD_DB")
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))

connection = psycopg2.connect(dbname='Clinics', user=USER, password=PASSWD_DB, host=HOST, port=PORT)
connection.autocommit = True
cursor = connection.cursor()

# создание и заполнение таблиц, создание триггера, индексов, процедуры
create_all_tables(cursor)
create_trigger(cursor)
insert_test_data(cursor)
create_indexes(cursor)
create_procedurs(cursor)

cursor.close() 
connection.close()
