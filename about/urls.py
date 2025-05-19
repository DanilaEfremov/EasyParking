from django.urls import path  # noqa: D100, EXE002

from about import views

urlpatterns = [
    path("", views.about, name="about"),                            # О нас  # noqa: RUF003
]
