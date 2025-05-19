#!/bin/sh

source /app/.venv/bin/activate;

python manage.py makemigrations;
python manage.py migrate;
#python manage.py collectstatic --noinput;
#python manage.py runserver 0.0.0.0:8000;
granian a_core.wsgi:application --host 0.0.0.0 --port 8000 --interface wsgi --workers 3 --no-ws --backlog 128
