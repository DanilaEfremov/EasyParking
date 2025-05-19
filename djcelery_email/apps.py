from django.apps import AppConfig  # noqa: D100, EXE002


class ContactsConfig(AppConfig):  # noqa: D101
    default_auto_field = "django.db.models.BigAutoField"
    name = "djcelery_email"
    verbose_name = "Отправка почты (Celery task)"
