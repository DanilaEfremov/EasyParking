from django.urls import path
from .. import views


urlpatterns = [
    path('', views.cart, name='cart'),                                                  # корзина покупателя
    path('<int:product_id>/add/', views.add_to_cart, name='add_to_cart'),               # добавление товара в корзину
    path('<int:product_id>/remove/', views.remove_from_cart, name='remove_from_cart'),  # удаление товара из корзины
    path('update/', views.update_cart, name='cart_update'),
    path('<int:item_id>/update/inc', views.item_increment, name='item_increment'),
    path('<int:item_id>/update/dec', views.item_decrement, name='item_decrement'),
    path('checkout/', views.checkout, name='checkout'),
    path('review/', views.checkout_final, name='review'),
]
