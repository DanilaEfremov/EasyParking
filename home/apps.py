from django.apps import AppConfig  # noqa: D100, EXE002


class HomeConfig(AppConfig):  # noqa: D101
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"
    verbose_name = "1. Главная"
