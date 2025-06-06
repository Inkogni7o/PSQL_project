# Система управления клиниками

Система управления клиниками — это веб-приложение, разработанное для управления данными клиник. Оно позволяет пользователям просматривать, обновлять, удалять и добавлять записи в различные таблицы базы данных.

## Описание

Этот проект предоставляет удобный интерфейс для взаимодействия с базой данных клиник. Основные функции включают:

- Просмотр данных из различных таблиц.
- Обновление существующих записей.
- Удаление записей.
- Добавление новых записей.

## Установка

Для запуска этого проекта на вашем локальном компьютере выполните следующие шаги:

### Предварительные требования

- Python 3.8 или выше
- PostgreSQL
- Установленные зависимости из файла `requirements.txt`

### Шаги установки

1. Клонируйте репозиторий на ваш локальный компьютер:

```bash
git clone <URL вашего репозитория>
```

2. Перейдите в директорию проекта:

```bash
cd <директория проекта>
```
3. Установите необходимые зависимости:
```bash
pip install -r requirements.txt
```
4. Настройте вашу базу данных PostgreSQL и обновите файл .env с вашими учетными данными для доступа к базе данных.
```
USER=<имя пользователя PostgreSQL>
PASSWD_DB=<пароль от пользователя>
HOST=<хост>
PORT=<порт>
```

5. Запустите приложение:
```bash
python src/main.py
```
### Использование
1. Откройте веб-браузер и перейдите по адресу http://<host>:<port>
2. Выберите таблицу из выпадающего списка для просмотра её содержимого
3. Используйте кнопки "Обновить", "Удалить" и "Добавить запись" для управления данными в таблице
