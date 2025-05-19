from django.urls import path  # noqa: D100, EXE002

from basket import views
from shop import views as shop_views

urlpatterns = [
    # List all products in user cart (GET)
    path("", views.basket, name="basket-list"),                                         # корзина покупателя

    # Create item in cart (POST)
    path("<int:product_id>/add/", views.create_item, name="create-basket-item"),      # добавление товара в корзину (одну штуку)  # noqa: E501
    path("<int:product_id>/add/<int:quantity>", views.create_item, name="create-basket-item"),# добавление товара в корзину  # noqa: E501

    # Read item (GET)
    path("<int:product_id>/qty/<int:quantity>", shop_views.product_detail, name="basket-item-detail"), # Просмотреть товар из корзины  # noqa: E501

    # Update item in cart (PATCH)
    path("<int:item_id>/inc/", views.item_increment, name="basket-item-increment"),   # Увеличить количество на 1
    path("<int:item_id>/dec/", views.item_decrement, name="basket-item-decrement"),   # Уменьшить количество на 1

    # Delete item from cart (DELETE)
    path("<int:item_id>/remove/", views.item_remove, name="remove-basket-item"),      # удаление товара из корзины
]
