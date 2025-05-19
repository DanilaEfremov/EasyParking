from django.conf import settings  # noqa: D100, EXE002
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from app.views import send_email

urlpatterns = [  # noqa: RUF005
    path("", include("home.urls")),                     # Главная страница
    path("admin/", admin.site.urls),                    # Панель администратора
    path("accounts/", include("accounts.urls")),        # Авторизация и учётные данные
    path("products/", include("shop.urls")),            # Товары, имеющиеся в магазине
    path("news/", include("news.urls")),                # Новости компании
    path("about/", include("about.urls")),              # О нас  # noqa: RUF003
    path("contacts/", include("contacts.urls")),        # Контакты
    path("send-email/", send_email, name="send-email"), #
    path("cart/", include("basket.urls")),                # Корзина покупателя
    path("order/", include("order.urls")),              # Заказы покупателя
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]




