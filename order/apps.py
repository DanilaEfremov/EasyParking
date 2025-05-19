from django.apps import AppConfig  # noqa: D100, EXE002


class OrderConfig(AppConfig):  # noqa: D101
    default_auto_field = "django.db.models.BigAutoField"
    name = "order"
    verbose_name = "8. Заказы"
