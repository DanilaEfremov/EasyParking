from django.apps import AppConfig  # noqa: D100, EXE002


class CartConfig(AppConfig):  # noqa: D101
    default_auto_field = "django.db.models.BigAutoField"
    name = "basket"
    verbose_name = "6. Карзина покупателя"
