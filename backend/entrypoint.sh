#!/bin/sh
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py upmodels data/data.json
gunicorn --bind 0:8000 foodgram.wsgi:application

exec "$@"