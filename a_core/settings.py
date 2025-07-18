"""
Django settings for a_core project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv

import structlog
from django.contrib import staticfiles

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
BUILD = "dev" if os.getenv("BUILD", "dev") == "dev" else "prod"
DEBUG = True if os.getenv("DEBUG", "False") == "True" and BUILD == "dev" else False

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# CSRF_TRUSTED_ORIGINS = [
#     'https://easyparking.local',
#     'https://*.your-other-trusted-domain.com',
#     # Wildcard для поддоменов
# ]


# Разрешить заголовки от прокси
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Если ты включаешь secure cookie
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

CSRF_TRUSTED_ORIGINS = ["https://easyparking.shop", "https://www.easyparking.shop"]



USE_THOUSAND_SEPARATOR = True


# Application definition

INSTALLED_APPS = [
    'constance',
    # 'django_daisy',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    "django_structlog",
    'storages',
    'cacheops',
    'django_cotton',
    'django_htmx',
    'simple_history',
    'djcelery_email',
    'django_celery_beat',

    'app',
    'shop',
    'news',
    'accounts',
]


AUTH_USER_MODEL = 'accounts.CustomUser'


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django_structlog.middlewares.RequestMiddleware",

    "django_htmx.middleware.HtmxMiddleware",
    'simple_history.middleware.HistoryRequestMiddleware',
]


if DEBUG:
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]
    INSTALLED_APPS += [
        'debug_toolbar',
    ]
    INTERNAL_IPS = ['127.0.0.1', ]

    # this is the main reason for not showing up the toolbar
    import mimetypes
    mimetypes.add_type("application/javascript", ".js", True)

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }


ROOT_URLCONF = 'a_core.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'a_core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'chat_db'),
        'USER': os.getenv('DB_USER', 'dan'),
        'PASSWORD': os.getenv('DB_PASSWORD', '1453'),
        'HOST': os.getenv('DB_HOST', 'db'),
        'PORT': os.getenv('DB_PORT', '5432'),
        "OPTIONS": {
            "pool": {
                "min_size": 5,
                "max_size": 10,
                "timeout": 30,
            }
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'a_core.validators.UppercasePasswordValidator',
    },
]

LOG_LEVEL = "INFO" if DEBUG else "WARNING"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
        },
        "plain_console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(),
        },
        "key_value": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.KeyValueRenderer(key_order=['timestamp', 'level', 'event', 'logger']),
        },
    },
    "handlers": {
        # Important notes regarding handlers.
        #
        # 1. Make sure you use handlers adapted for your project.
        # These handlers configurations are only examples for this library.
        # See python's logging.handlers: https://docs.python.org/3/library/logging.handlers.html
        #
        # 2. You might also want to use different logging configurations depending of the environment.
        # Different files (local.py, tests.py, production.py, ci.py, etc.) or only conditions.
        # See https://docs.djangoproject.com/en/dev/topics/settings/#designating-the-settings
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "plain_console",
        },
        "json_file": {
            "class": "logging.handlers.WatchedFileHandler",
            "filename": "logs/json.log",
            "formatter": "json_formatter",
        },
        "flat_line_file": {
            "class": "logging.handlers.WatchedFileHandler",
            "filename": "logs/flat_line.log",
            "formatter": "key_value",
        },
    },
    "root": {
        "handlers": ["console", "flat_line_file", "json_file"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django_structlog": {
            "handlers": ["console", "flat_line_file", "json_file"],
            "level": LOG_LEVEL,
        },
        "django_structlog_a_core": {
            "handlers": ["console", "flat_line_file", "json_file"],
            "level": LOG_LEVEL,
        },
    }
}

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)


LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)






# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = os.getenv('TZ', 'Europe/Moscow')

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": os.getenv("S3_ACCESS_KEY"),
            "secret_key": os.getenv("S3_SECRET_KEY"),
            "bucket_name": os.getenv("S3_BUCKET_NAME"),
            "url_protocol": "http:",
            "custom_domain": os.getenv("S3_CUSTOM_DOMAIN"),
            "querystring_auth": False,
            "endpoint_url": os.getenv("S3_ENDPOINT_URL"),
            "use_ssl": os.getenv("S3_USE_SSL", "False") == "True",
            "default_acl": os.getenv("S3_DEFAULT_ACL", "public-read"),
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'

MEDIA_ROOT = 'media'
MEDIA_URL= 'http://minio:9000/'


STATIC_URL = '/static/'
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'), ]
# STATIC_ROOT = BASE_DIR / 'static'
STATIC_ROOT  = os.path.join(BASE_DIR, 'static')



# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
# EMAIL_HOST_USER = 'mr.dan.efremov@gmail.com'  # Ваш email-адрес
# EMAIL_HOST_PASSWORD = 'pveo cmsb rige ixcq'  # Пароль от email
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "easyparking673@gmail.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Celery
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

# Celery beat
CELERY_BEAT_SCHEDULE_FILENAME = "celerybeat-schedule.db"



# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Constance
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
CONSTANCE_CONFIG = {
    'TIME_TO_CANCEL_ORDER': (10 * 24 * 60 * 60, 'Время в секундах через которое заказ автоматически отменится'),
    'EMAIL': ('easyparking673@gmail.com', 'Email компании'),
    'PASSWORD': ('gjti pwke upcr qnzm', 'Пароль приложения почтового ящика'),
}




CACHEOPS_REDIS = {
    "host": os.getenv("CACHE_REDIS_HOST", "redis"),
    "port": int(os.getenv("CACHE_REDIS_PORT", 6379)),
    "db": int(os.getenv("CACHEOPS_REDIS_DB", 1)),
    "socket_timeout": 3,
}


CACHEOPS = {
# Automatically cache any User.objects.get() calls for 15 minutes
    # This also includes .first() and .last() calls,
    # as well as request.user or post.author access,
    # where Post.author is a foreign key to auth.User
    'auth.user': {'ops': 'get', 'timeout': 60*15},

    # Automatically cache all gets and queryset fetches
    # to other django.contrib.auth models for an hour
    # 'auth.*': {'ops': {'fetch', 'get'}, 'timeout': 60*60},

    # Cache all queries to Permission
    # 'all' is an alias for {'get', 'fetch', 'count', 'aggregate', 'exists'}
    'auth.permission': {'ops': 'all', 'timeout': 60*60},

    # Cache all queries to News
    # 'all' is an alias for {'get', 'fetch', 'count', 'aggregate', 'exists'}
    'news.*': {'ops': 'all', 'timeout': 60 * 60},

    # Cache all queries to Shop
    # 'all' is an alias for {'get', 'fetch', 'count', 'aggregate', 'exists'}
    'shop.*': {'ops': 'all', 'timeout': 60 * 5},

    # Enable manual caching on all other models with default timeout of an hour
    # Use Post.objects.cache().get(...)
    #  or Tags.objects.filter(...).order_by(...).cache()
    # to cache particular ORM request.
    # Invalidation is still automatic
    # '*.*': {'ops': 'all', 'timeout': 60*3},

    # And since ops is empty by default you can rewrite last line as:
    # '*.*': {'timeout': 60*60},

    # NOTE: binding signals has its overhead, like preventing fast mass deletes,
    #       you might want to only register whatever you cache and dependencies.

    # Finally you can explicitely forbid even manual caching with:
    # 'some_app.*': None,
}


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{os.getenv('CACHE_REDIS_HOST', 'redis')}:{os.getenv('CACHE_REDIS_PORT', 6379)}",
        "OPTIONS": {
            "db": int(os.getenv("DJANGO_CACHE_REDIS_DB", 2)),
        },
    }
}

