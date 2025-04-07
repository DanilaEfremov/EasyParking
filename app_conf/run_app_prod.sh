#!/bin/sh

#python manage.py migrate;
python manage.py collectstatic --noinput;
#python manage.py runserver 0.0.0.0:8000;

gunicorn --workers 3 --bind 0.0.0.0:8000 a_core.wsgi:application
# gunicorn -w 2 -b 0:8000 web_app.wsgi:application;
