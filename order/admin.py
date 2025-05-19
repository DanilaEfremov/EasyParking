from django.contrib import admin  # noqa: D100, EXE002

from order.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Встроенная модель для отображения товаров внутри заказа."""

    model = OrderItem
    readonly_fields = ("product_id", "name", "description", "quantity", "price")
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None) -> bool:  # noqa: ANN001, ARG002, D102
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Настройки админки для заказов."""

    list_display = ("id", "user", "email", "created_at", "status", "total_price")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "id", "email")
    ordering = ("-created_at",)
    exclude = ["full_name"]  # noqa: RUF012
    readonly_fields = (
        "user", "email", "created_at", "total_price", "zip_code", "city", "address", "recipient", "comment"
    )
    inlines = [OrderItemInline]  # noqa: RUF012

    def formfield_for_choice_field(self, db_field, request, **kwargs):  # noqa: ANN003, ANN001, ANN201, D102
        if db_field.name == "status":
            allowed_choices = ["pending", "completed", "canceled"]  # Укажите допустимые значения
            kwargs["choices"] = [
                choice for choice in db_field.choices if choice[0] in allowed_choices
            ]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def has_delete_permission(self, request, obj=None) -> bool:  # noqa: ANN001, ARG002, D102
        return False

    def get_readonly_fields(self, request, obj=None):  # noqa: ANN201, ANN001, ARG002, D102
        # if obj and (obj.status == "canceled" or obj.status == "canceled_automatically") or obj.status == "completed":
        if (obj and (obj.status in {"canceled", "canceled_automatically"})) or obj.status == "completed":
            return [field.name for field in obj._meta.fields]  # noqa: SLF001
        return self.readonly_fields


# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     """Настройки админки для товаров в заказе"""
#     list_display = ("order", 'product_id',"name", "description", "quantity", "price")
#     readonly_fields = ("order", 'product_id', "name", "description", "quantity", "price")
#
#     search_fields = ("order__id", "name",)
