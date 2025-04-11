#!/bin/sh

#chown -R myuser:myuser /app/logs
#chmod -R 755 /app/logs


python manage.py makemigrations;
python manage.py migrate;
python manage.py collectstatic --noinput;
python manage.py runserver 0.0.0.0:8000;
