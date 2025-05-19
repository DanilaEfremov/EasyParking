from django.contrib import admin  # noqa: D100, EXE002

from .models import News

admin.site.register(News)
