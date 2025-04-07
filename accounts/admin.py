# from django.contrib import admin
#
# from .models import CustomUser
#
# admin.site.register(CustomUser)


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile


class ProfileInline(admin.StackedInline):
    """Позволяет редактировать профиль пользователя в админке."""
    model = Profile
    can_delete = False
    verbose_name_plural = "Профиль"


class CustomUserAdmin(UserAdmin):
    """Кастомное отображение модели CustomUser в админке."""
    model = CustomUser
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)

    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Личная информация", {"fields": ("first_name", "last_name", "middle_name", "birth_date")}),
        ("Разрешения", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )

    inlines = [ProfileInline]  # Включаем профиль в редактирование пользователя


# Регистрируем модели в админке
admin.site.register(CustomUser, CustomUserAdmin)