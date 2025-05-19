from django.apps import AppConfig  # noqa: D100, EXE002


class AboutConfig(AppConfig):  # noqa: D101
    default_auto_field = "django.db.models.BigAutoField"
    name = "about"
    verbose_name = "4. О нас"  # noqa: RUF001
