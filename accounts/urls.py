from django.urls import path  # noqa: D100, EXE002

from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),    # Регистрация
    path("login/", views.login_view, name="login"),             # Авторизация
    path("logout/", views.logout_view, name="logout"),          # Выход

    path("my/", views.account, name="account"),                 # Мой аккаунт
    path("my/person_change/", views.account_personal_change, name="account-personal-data-change"),
    path("my/password_change/", views.account_password_change, name="account-password-change"),
    path("my/address_change/", views.account_address_change, name="account-address-change"),
]
