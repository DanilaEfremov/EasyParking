# Интернет магазин

Этот проект представляет собою интернет магазин, где пользователи могут покупать товары и добавлять их в корзину.
Также есть раздел с новостями. 



## Используемые технологии
1. Django (https://djangoproject.com[](https://www.djangoproject.com))
2. Postgres (https://www.postgresql.org[](https://www.postgresql.org))
3. Angie (https://angie.software[](https://angie.software/))
4. Celery (https://docs.celeryq.dev[](https://docs.celeryq.dev/en/stable/))
5. Minio (https://m in.io[](https://min.io))
6. Valkey (https://valkey.io[](https://valkey.io))

## Используемые инструменты
Приложение разворачивается с помощью Docker-композера.
Для симуляции одностраничного приложения был использован HTMX, который позволяет делать запросы без перезагрузки страницы.

## Установка и запуск
Для установки зависимостей и запуска проекта выполните следующие команды:

```sh
# Клонировать проект из GitHub
git clone https://github.com/danefremov/shopping.git

# Перейти в директорию проекта
cd ./shopping/mysite

# Запустите Docker-композер из директории ros_chat
docker compose up --build

# Запустите миграции базы данных
docker compose exec web python manage.py migrate

# Создайте суперпользователя
docker compose exec web python manage.py createsuperuser

Возможно надо проверить angine.conf

Поменять конфигурацию .env для minio и создать bucket

Настроить демоны автозапуска 

Пароль flower:  htpasswd -c ./app_conf/angie/.htpasswd dan

Чтобы без sudo жми sudo usermod -aG docker $USER

# Запустите сервер в режиме реального времени
Можно переходить по ссылке для просмотра сайта.
```

