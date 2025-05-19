from django.urls import path  # noqa: D100, EXE002

from order import views

urlpatterns = [
    path("checkout/", views.checkout, name="cart-checkout"),
    path("review/", views.checkout_final, name="cart-review"),
]
