from shop import models as shop_models  # noqa: D100, EXE002


class Order(shop_models.Order):
    """Заказ пользователя.

    Attributes:
        user (ForeignKey): Покупатель.
        total_price (DecimalField): Общая сумма заказа.
        created_at (DateTimeField): Дата оформления заказа.
        status (CharField): Статус заказа.

    """

    class Meta:  # noqa: D106
        proxy = True
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderItem(shop_models.OrderItem):
    """Товары в заказе.

    Attributes:
        order (ForeignKey): Связанный заказ.
        product (ForeignKey): Купленный товар.
        quantity (PositiveIntegerField): Количество.
        price (DecimalField): Цена товара на момент покупки.

    """

    class Meta:  # noqa: D106
        proxy = True
        verbose_name = "Товар заказа"
        verbose_name_plural = "Товары заказа"
