from django.apps import AppConfig  # noqa: D100, EXE002


class AccountsConfig(AppConfig):  # noqa: D101
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "7. Покупатели"
    icon = "fa fa-users"
