from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register_view, name='register'),    # Регистрация
    path('login/', views.login_view, name='login'),             # Авторизация
    path('logout/', views.logout_view, name='logout'),          # Выход
    path('my/', views.account, name='account'),                 # Мой аккаунт
    path('my/account_personal_change/', views.account_personal_change, name='account_personal_change'),
    path('my/account_password_change/', views.account_password_change, name='account_password_change'),
    path('my/account_adress_change/', views.account_address_change, name='account_address_change'),
]
