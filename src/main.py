import os
import psycopg2
from dotenv import load_dotenv

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
cursor.execute('CREATE TABLE test_table(test date);')
cursor.close() 
connection.close()


