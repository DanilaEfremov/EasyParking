from django.urls import path  # noqa: D100, EXE002

from contacts import views

urlpatterns = [
    path("", views.contacts, name="contacts"),                   # Контакты
]




