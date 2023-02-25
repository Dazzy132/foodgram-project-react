FROM python:3.7-slim

WORKDIR /app/backend

COPY . /app/backend/

RUN pip3 install -r ./requirements.txt --no-cache-dir

#CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]
