import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for

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

cursor.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'; """)
tables = [i[0] for i in cursor.fetchall()]

# создание и заполнение таблиц, создание триггера, индексов, процедуры
create_all_tables(cursor)
# create_trigger(cursor)
# insert_test_data(cursor)
create_indexes(cursor)
create_procedurs(cursor)

app = Flask(__name__)

@app.route('/')
def index(): 
    return render_template("choice.html", tables=tables)

@app.route('/tables')
def display_tables():
    cursor.execute("SELECT * FROM Clinics")
    data = cursor.fetchall()
    return render_template("tables2.html", data=data)

@app.route('/display_table', methods=['POST'])
def display_table():
    table_name = request.form.get('table_name')
    if table_name not in tables:
        return redirect(url_for('index'))
    cursor.execute(f"SELECT * FROM {table_name}")
    data = cursor.fetchall()
    return render_template("tables.html", table_name=table_name, data=data)

if __name__ == '__main__':
    app.run(debug=True)