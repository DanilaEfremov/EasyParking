from django.urls import path  # noqa: D100, EXE002

from news import views

urlpatterns = [
    path("", views.news, name="news"),                                # Новости компании
    path("<int:news_id>/", views.news_detail, name="news-detail"),    # Детали новости
]
