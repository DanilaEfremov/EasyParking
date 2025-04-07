from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Product, ProductImage, Order, OrderItem


class ProductImageInline(admin.TabularInline):
    """Позволяет добавлять дополнительные фотографии прямо на странице товара."""
    model = ProductImage
    extra = 1


class StockFilter(admin.SimpleListFilter):
    title = 'Товар в наличии'
    parameter_name = 'stock_filter'

    def lookups(self, request, model_admin):
        return (
            ('in_stock', 'в наличии'),
            ('out_of_stock', 'нет на складе'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'in_stock':
            return queryset.filter(stock__gt=0)
        elif self.value() == 'out_of_stock':
            return queryset.filter(stock=0)


class ProductAdmin(SimpleHistoryAdmin):
    """Настройка отображения модели Product в админке."""
    list_display = ('name', 'price', 'stock', 'show_in_catalog')
    ordering = ("price",)
    list_filter = ('show_in_catalog', StockFilter,)
    history_list_display = ["price", "stock"]
    inlines = [ProductImageInline]



admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)


class OrderItemInline(admin.TabularInline):
    """Встроенная модель для отображения товаров внутри заказа"""
    model = OrderItem
    readonly_fields = ('product_id', "name", "description", "quantity", "price")
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Настройки админки для заказов"""
    list_display = ("id", "user", "total_price", "status", "email", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "id", "email")
    ordering = ("-created_at",)
    readonly_fields = ("user", "total_price", "email", "created_at", "recipient", "address", "city", "zip_code", "comment", "full_name")
    inlines = [OrderItemInline]

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "status":
            allowed_choices = ['pending', 'approved', 'completed', 'canceled']  # Укажите допустимые значения
            kwargs["choices"] = [
                choice for choice in db_field.choices if choice[0] in allowed_choices
            ]
        return super().formfield_for_choice_field(db_field, request, **kwargs)


    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj and (obj.status == "canceled" or obj.status == "canceled_automatically") or obj.status == "completed":
            return [field.name for field in obj._meta.fields]
        return self.readonly_fields


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Настройки админки для товаров в заказе"""
    list_display = ("order", 'product_id',"name", "description", "quantity", "price")
    readonly_fields = ("order", 'product_id', "name", "description", "quantity", "price")

    search_fields = ("order__id", "name")