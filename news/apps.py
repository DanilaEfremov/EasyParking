from django.apps import AppConfig  # noqa: D100, EXE002


class NewsConfig(AppConfig):  # noqa: D101
    default_auto_field = "django.db.models.BigAutoField"
    name = "news"
    verbose_name = "3. Новости"
    icon = "fa-solid fa-newspaper"
