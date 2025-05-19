from django.urls import path  # noqa: D100, EXE002

from home import views

urlpatterns = [
    path("", views.home, name="home"),    # Главная страница
]
