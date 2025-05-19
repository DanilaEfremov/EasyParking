from django.apps import AppConfig  # noqa: EXE002


class ShopConfig(AppConfig):  # noqa: D101
    default_auto_field = "django.db.models.BigAutoField"
    name = "shop"
    verbose_name = "2. Каталог товаров"
    icon = "fa fa-shopping-cart"
