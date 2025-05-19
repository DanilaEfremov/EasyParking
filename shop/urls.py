from django.urls import path  # noqa: D100, EXE002

from . import views

urlpatterns = [
    # Read (GET)
    path("", views.products, name="products-list"),                         # Список товаров
    # re_path(r'^(?P<product_id>\d+)(?:/qty/(?P<quantity>\d+))?/$', views.product_detail, name='product-detail'),
    path("<int:product_id>/", views.product_detail, name="product-detail"), # Детальное описание товара

    # Update (PATCH)
    path("<int:product_id>/inc/<int:quantity>", views.product_increment, name="product-increment"),
    path("<int:product_id>/dec/<int:quantity>", views.product_decrement, name="product-decrement"),
]

