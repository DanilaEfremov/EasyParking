from datetime import datetime  # noqa: D100, EXE002
from typing import ClassVar

from cacheops import invalidate_model
from constance import config
from django.db import models, transaction
from simple_history.models import HistoricalRecords

from a_core import settings
from a_core.celery import set_automatically_canceled


class Product(models.Model):
    """Товар магазина.

    Attributes:
        name (str): Название товара
        description (str): Описание товара
        image (ImageField): Изображение товара
        price (DecimalField): Цена товара
        stock (PositiveIntegerField): Количество товара на складе
        created_at (DateTimeField): Дата создания.

    """

    name = models.CharField(verbose_name="Название товара", max_length=255)
    description = models.TextField(verbose_name="Описание товара")
    image = models.ImageField(verbose_name="Фото товара", upload_to="products/")  # Путь для изображения
    price = models.DecimalField(verbose_name="Цена товара", max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(verbose_name="Количество на складе", default=0)
    show_in_catalog = models.BooleanField(verbose_name="Показывать в каталоге", default=True)
    created_at = models.DateTimeField(verbose_name="Дата создания учётной карточки товара", auto_now_add=True)
    history = HistoricalRecords()

    class Meta:  # noqa: D106
        verbose_name = "Товар магазина"
        verbose_name_plural = "Товары магазина"


    def __str__(self) -> str:  # noqa: D105
        return self.name


class ProductImage(models.Model):
    """Дополнительное изображение товара.

    Attributes:
        product (ForeignKey): Товар
        image (ImageField): Изображение.

    """

    product = models.ForeignKey(Product, related_name="additional_images", on_delete=models.CASCADE, verbose_name="Товар")  # noqa: E501
    image = models.ImageField(verbose_name="Дополнительное изображение", upload_to="products/additional/")

    class Meta:  # noqa: D106
        verbose_name = "Дополнительное изображение"
        verbose_name_plural = "Дополнительные изображения"

    def __str__(self) -> str: return self.image.name  # noqa: D105


class Cart(models.Model):
    """Корзина покупателя.

    Attributes:
        user (ForeignKey): Покупатель

    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Покупатель")

    class Meta:  # noqa: D106
        verbose_name = "Корзина покупателя"

    def __str__(self) -> str: return f"Cart of {self.user.username}"  # noqa: D105


class CartItem(models.Model):
    """Товар в корзине покупателя.

    Attributes:
        cart (ForeignKey): Корзина покупателя
        product (ForeignKey): Товар
        quantity (PositiveIntegerField): Количество товара

    """

    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE, verbose_name="Корзина покупателя")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:  # noqa: D106
        verbose_name = "Товар в корзине покупателя"
        verbose_name_plural = "Товары в корзине покупателя"

    def __str__(self) -> str:  # noqa: D105
        return f"{self.quantity} x {self.product.name}"

    def save(self, *args, **kwargs) -> None:  # noqa: D102, ANN002, ANN003
        if self.quantity > self.product.stock:
            msg = "Недостаточно товаров на складе"
            raise ValueError(msg)
        super().save(*args, **kwargs)


class Order(models.Model):
    """Заказ пользователя.

    Attributes:
        user (ForeignKey): Покупатель
        total_price (DecimalField): Общая сумма заказа
        created_at (DateTimeField): Дата оформления заказа
        status (CharField): Статус заказа

    """

    STATUS_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("pending", "В обработке"),  # noqa: RUF001
        ("completed", "Завершён"),
        ("canceled", "Отменён"),
        ("canceled_automatically", "Автоматическая отмена"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Покупатель")
    email = models.EmailField(verbose_name="Информация направлена на почту", max_length=255)
    full_name = models.CharField(verbose_name="Полное имя", max_length=255)
    address = models.CharField(verbose_name="Адрес", max_length=255)
    city = models.CharField(verbose_name="Город", max_length=255)
    zip_code = models.CharField(verbose_name="Почтовый индекс", max_length=10)
    recipient = models.CharField(verbose_name="Получатель", max_length=255)
    comment = models.TextField(verbose_name="Комментарий к заказу", blank=True)
    total_price = models.DecimalField(verbose_name="Общая сумма", max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(verbose_name="Дата заказа", auto_now_add=True)
    status = models.CharField(verbose_name="Статус", max_length=25, choices=STATUS_CHOICES, default="pending")

    class Meta:  # noqa: D106
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self) ->str:  # noqa: D105
        return f"Заказ №{self.id}.  Покупатель {self.user}.  ({self.get_status_display()})"

    @transaction.atomic
    def save(self, *args, **kwargs) -> None:  # noqa: D102, ANN002, ANN003
        def planned_auto_cancel(order_id: int) -> None:
            """Запустить задачу по отмене выполнения заказа."""
            if 18 > datetime.now().hour >= 9:  # noqa: DTZ005, PLR2004
                time = config.TIME_TO_CANCEL_ORDER # дни в секундах
            else:
                time = config.TIME_TO_CANCEL_ORDER + (9 + (24 - datetime.now().hour)) * 60 * 60  # 10 дней + время до 9 утра сл дня  # noqa: DTZ005, E501
            set_automatically_canceled.apply_async((order_id, "canceled_automatically"), countdown=time, retry=True)

        if self.pk:
            saved_status = Order.objects.get(pk=self.pk).status
            # if (saved_status != 'canceled' and saved_status != 'canceled_automatically') and (
                    # self.status == 'canceled' or self.status == 'canceled_automatically'):
            if (saved_status not in {"canceled", "canceled_automatically"}) and (self.status in {"canceled", "canceled_automatically"}):  # noqa: E501
                products_for_update = []
                for item in self.items.all():
                    product = Product.objects.get(id=item.product_id)
                    product.stock += item.quantity
                    products_for_update.append(product)
                Product.objects.bulk_update(products_for_update, ["stock"])
        super().save(*args, **kwargs)
        invalidate_model(Product)
        if self.status == "pending":
            planned_auto_cancel(self.pk)

    @classmethod
    def get_order_statuses(cls) -> list[tuple[str, str]]:
        """Возвращает список зарегистрированных статусов заказа."""
        return cls.STATUS_CHOICES

    @classmethod
    def is_status_name_valid(cls, status_name: str) -> bool:
        """Проверяет, существует ли такой статус заказа."""
        return any(status[0] == status_name for status in cls.get_order_statuses())


class OrderItem(models.Model):
    """Товары в заказе.

    Attributes:
        order (ForeignKey): Связанный заказ
        product_id (PositiveIntegerField): Купленный товар
        name (CharField): Название товара
        description (CharField): Описание товара
        quantity (PositiveIntegerField): Количество
        price (DecimalField): Цена товара на момент покупки.

    """

    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE, verbose_name="Заказ")
    product_id = models.PositiveIntegerField(verbose_name="id Товара", default=0)
    name = models.CharField(verbose_name="Название товара", max_length=255)
    description = models.TextField(verbose_name="Описание товара")
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.DecimalField(verbose_name="Цена товара", max_digits=10, decimal_places=2)

    class Meta:  # noqa: D106
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказе"

    def __str__(self) -> str: return f"{self.quantity} x {self.name} (Заказ {self.order.id})"  # noqa: D105
