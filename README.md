# Продуктовый помощник (дипломный проект)

![foodgram workflow](https://github.com/dazzy132/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## 📄 Описание проекта:

### Проект "Продуктовый помощник" это онлайн-сервис на котором пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

--------------------------------------------------------


## 🔧 Инструменты разработки:


[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org)
[![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com)
[![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)](https://www.django-rest-framework.org)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)


### Технологический стек (Backend):
- Python - 3.7
- Django - 3.2.18
- Django Rest Framework - 3.14.0
- Djoiser - 2.1.0
- Gunicorn - 20.1.0


-----------------------------------------------------------

## Варианты установки проекта

## 1. Локально (Без Docker)

### Наполнение .env-файла

```dotenv
SECRET_KEY="your-secret-key"
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

##### 1) Клонировать репозиторий

```
git clone git@github.com:Dazzy132/foodgram-project-react.git
```

##### 2) Создать виртуальное окружение проекта

```
python -m venv venv
```

##### 3) Активировать виртуальное окружение

```
source venv/bin/activate
```

##### 4) Установить зависимости проекта

```
pip install -r requirements.txt
```

##### 5) Выполнить команду для выполнения миграций
```
python manage.py migrate
```

##### 6) Заполнить базу данных тестовыми данными (По желанию)
```
python manage.py loaddata data/data.json
```

##### 7) Создать суперпользователя
```
python manage.py createsuperuser
```

##### 8) Запустить сервер
```
python manage.py runserver
```

## 2. С Docker контейнерами

### Наполнение .env-файла
```dotenv
SECRET_KEY="your-secret-key"
DB_ENGINE=django.db.backends.postgresql_psycopg2
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST="db"
DB_PORT=5432
```

### Команды для докера

```shell
cd foodgram-project-react/infra/
docker-compose up -d --build
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --no-input
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py loaddata data/data.json
```
