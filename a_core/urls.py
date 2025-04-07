from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from app.views import about, contacts, send_email
from news.views import home, news_detail, news


urlpatterns = [
    path('', home, name='home'),                                    # Главная страница
    path('admin/', admin.site.urls),                                # Панель администратора
    path('accounts/', include('accounts.urls')),                    # Авторизация и учётные данные

    path('products/', include('shop.urls.products')),               # Товары, имеющиеся в магазине
    path('cart/', include('shop.urls.cart')),                       # Корзина покупателя

    path('news/', news, name='news'),
    path('news/<int:news_id>/', news_detail, name='news_detail'),   # Детали новости

    path('about/', about, name='about'),                            # О нас
    path('contacts/', contacts, name='contacts'),                   # Контакты
    path('send-email/', send_email, name='send_email'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]




