# from django.db import models  # noqa: D100, EXE002

from shop import models as shop_models


class Basket(shop_models.Cart):
    """Корзина покупателя.

    Attributes:
        user (ForeignKey): Покупатель.

    """

    class Meta:  # noqa: D106
        proxy = True


class BasketItem(shop_models.CartItem):
    """Товар в корзине покупателя.

    Attributes:
        cart (ForeignKey): Корзина покупателя
        product (ForeignKey): Товар
        quantity (PositiveIntegerField): Количество товара

    """

    class Meta:  # noqa: D106
        proxy = True
