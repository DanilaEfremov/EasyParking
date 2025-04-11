# Переменные окружения
Будьте аккуратны.
От правильности переменных окружения зависит сборка образов и работа контейнеров проекта.


## 1. Режим сборки Docker образов и режим работы
Предусмотрено два режима сборки:
  - для разработки и отладки;
  - для работы.

За выбор режима сборки отвечает переменная `BUILD`.  
Она может принимать только два значения:
  - для разработки и отладки:
```dotenv
BUILD=dev
```
  - для работы:
```dotenv
BUILD=prod
```

> [!IMPORTANT]
> Переменная `BUILD` влияет на поведение переменной `DEBUG`.  При значении `BUILD=prod` `DEBUG` всегда равна `False`.

## 2. Django
В этот раздел входят следующие переменные окружения:
```dotenv
# Django
YOU_DOMAIN=localhost
SECRET_KEY=django-insecure-y7b*so7g4fy4+5-8!7sl$j%^glmz$&&5flzu4z5*y++=fu1&y!
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost,.${YOU_DOMAIN},
LANGUAGE=ru_RU
TZ=Europe/Moscow
```
> [!IMPORTANT]
> Не забывайте, что на `DEBUG` влияет `BUILD`.  При значении `BUILD=prod` `DEBUG` всегда равна `False`. <br/>
> Не забудте поменять `YOU_DOMAIN` на ваш домен.


### 2.1 Переменные для контейнера Django
Для того чтобы запустить Django не под root, созданы следующие переменные:
```dotenv
D_USER=djangouser
D_GROUP=djangogroup
D_UID=1000
D_GID=1002
```
Этот функционал пока не реализован и будет сделан в дальнейшем.

### 2.2 Пакет django-cacheops, как кэш запросов к СУБД

```dotenv
# Cacheops
CACHE_REDIS_PORT=6379
CACHEOPS_REDIS_DB=1
```

### 2.3 Кэш Django
Встроеный в `Django` механизм используется для кэширования шаблонов и представлений.
```dotenv
# Кэширование
CACHE_REDIS_HOST=redis
# Пароль для Redis (имя пользователя по умолчанию - default).
# REDIS_PASSWORD=1453
# Имя нового пользователя.
# REDIS_USER=dan
# Пароль для нового пользователя.
# REDIS_USER_PASSWORD=1453
DJANGO_CACHE_REDIS_DB=2
```

### 2.4 Бакенд для системы кэширования
Для Cachops и для встроеного механизма кэширования используется форк `Redis` - `Valkey`.
Настроек пока нет.

### 2.5 Отправка электронной почты
```dotenv
# Почта
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=easyparking673@gmail.com
EMAIL_HOST_PASSWORD='gjti pwke upcr qnzm'
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

## 3. СУБД 
### 3.1 Postgres
Проектом используется Postgres, как основная система управления базами данных.
Запускается в отдельном контейнере.
Для конфигурирования Postgres в Docker compose используются следующие переменные:
```dotenv
# Postgres
DB_HOST=db
DB_USER=dan
DB_PASSWORD=1453
DB_PORT=5432
DB_NAME=chat_db
```

> [!NOTE]
> Эти переменные так же используются для конфигурирования связи Django с Postgres в настройках проекта Django.

Помимо этого для конфигурирования Postgres используются переменный `TZ` и `LANGUAGE` из раздела Django.

Пример docker-compose.yml:
```yaml
  db:
    hostname: ${DB_HOST}
    restart: unless-stopped
    image: postgres:17.4-alpine3.21
    container_name: db
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      LANG: ${LANGUAGE}.UTF-8
      LANGUAGE: ${LANGUAGE}.UTF-8
      TZ: ${TZ}
    env_file:
      - .env
```

### 3.2 PGAdmin  
В качестве программы для администрирования Postgres используется PGAdmin.  
Ниже приведены настройки для него:
```dotenv
# PGAdmin
PGADMIN_DEFAULT_EMAIL=mr.dan.efremov@me.com
PGADMIN_DEFAULT_PASSWORD=1234
PGADMIN_CONFIG_SERVER_MODE=False
```

## 4. Хранение медиа файлов
Так как при развёртывании проекта в дата-центрах вероятен вариант отсутствия возможности записи в файловую систему
напрямую, то для работы с медиафайлами выбран для использования в качестве бакенда хранилище объектов `S3`.
В качестве промежуточного ПО взят проект `django-storages`, а в качестве бакенда `Minio`. 
Ниже перечислены переменные, которые используются для настройки как `django-storages`, так и `Minio`:
```dotenv
# MINIO - Хранилище S3 для медиафайлов
S3_HOST=minio
MINIO_ROOT_USER: minioadmin
MINIO_ROOT_PASSWORD: minioadmin
MINIO_PORT=9000
S3_ACCESS_KEY=R1V728o6z3yT465Kwxz1
S3_SECRET_KEY=DZExgEncPm6gqsFXYi2xzmRc26TbPAmv7R0L7UGm
S3_BUCKET_NAME=media
S3_ENDPOINT_URL=http://${S3_HOST}:${MINIO_PORT}
S3_CUSTOM_DOMAIN=${YOU_DOMAIN}/minio/s3/${S3_BUCKET_NAME}
S3_USE_SSL=False
S3_DEFAULT_ACL=public-read
MINIO_BROWSER_REDIRECT_URL=http://${S3_HOST}/minio/ui
```

## 5. Ассинхронное выполнение задач, поставленных в очередь
### 5.1  Celery
Для целей выполнения фоновых задач используется Celery, настройки которого приведены ниже;
```dotenv
# Celery
CELERY_BROKER_URL=pyamqp://${RABBITMQ_DEFAULT_USER}:${RABBITMQ_DEFAULT_PASS}@${RABBITMQ_HOST}:5672//
```

### 5.2 RabbitMQ, как бакенд для Celery
```dotenv
# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_DEFAULT_USER=guest
RABBITMQ_DEFAULT_PASS=guest
```

### 5.3 Flower, мониторинг Celery
```dotenv
# Flower
FLOWER_USER=admin
FLOWER_PASSWORD=admin
# FLOWER_BASIC_AUTH=${FLOWER_USER}:${FLOWER_PASSWORD}
FLOWER_BROKER_API="http://${RABBITMQ_DEFAULT_USER}:${RABBITMQ_DEFAULT_PASS}@${RABBITMQ_HOST}:15672/api/"
FLOWER_XHEADERS=True
FLOWER_URL_PREFIX=/flower
```

> [!TIP]
> Если вам нужна аутентификация для доступа к `Flower` и вы не убираете его за обратный прокси сервер, то раскоментируйте `FLOWER_BASIC_AUTH`. 

> [!NOTE]
> Useful information that users should know, even when skimming content.

> [!TIP]
> Helpful advice for doing things better or more easily.

> [!IMPORTANT]
> Key information users need to know to achieve their goal.

> [!WARNING]
> Urgent info that needs immediate user attention to avoid problems.

> [!CAUTION]
> Advises about risks or negative outcomes of certain actions.
> 