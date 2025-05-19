from typing import ClassVar  # noqa: D100, EXE002

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from simple_history.admin import SimpleHistoryAdmin

from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    """Позволяет добавлять дополнительные фотографии прямо на странице товара."""

    model = ProductImage
    extra = 1


class StockFilter(admin.SimpleListFilter):
    """Фильтр товаров в админке."""

    title = "Товар в наличии"
    parameter_name = "stock_filter"

    def lookups(self, request, model_admin):  # noqa: ANN201, ANN001, ARG002, D102
        return (
            ("in_stock", "в наличии"),
            ("out_of_stock", "нет на складе"),
        )

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:  # noqa: ARG002, D102
        if self.value() == "in_stock":
            return queryset.filter(stock__gt=0)
        if self.value() == "out_of_stock":
            return queryset.filter(stock=0)
        return queryset


class ProductAdmin(SimpleHistoryAdmin):
    """Настройка отображения модели Product в админке."""

    list_display: tuple[str] = ("name", "price", "stock", "show_in_catalog")
    ordering: tuple[str] = ("price",)
    list_filter = ("show_in_catalog", StockFilter,)
    history_list_display: ClassVar[list[str]] = ["price", "stock"]
    inlines = [ProductImageInline]



admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
