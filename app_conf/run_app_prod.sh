#!/bin/sh

#python manage.py migrate;
python manage.py collectstatic --noinput;

#gunicorn --workers 3 --bind 0.0.0.0:8000 a_core.wsgi:application
granian a_core.wsgi:application --host 0.0.0.0 --port 8000 --interface wsgi --workers 3 --no-ws --backlog 128
