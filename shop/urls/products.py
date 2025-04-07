from django.urls import path, re_path
from .. import views


urlpatterns = [
    path('', views.products, name='products'),                                  # список товаров
    re_path(r'^(?P<product_id>\d+)(?:/(?P<quantity>\d+))?/$', views.product_detail, name='product_detail'),
    path('<int:product_id>/inc/<int:quantity>', views.product_increment, name='product_increment'),
    path('<int:product_id>/dec/<int:quantity>', views.product_decrement, name='product_decrement'),
]
