from django.contrib import messages  # noqa: D100, EXE002
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404

from basket.models import BasketItem


def calculate_basket_total(request) -> (int, int):  # noqa: ANN001
    """Вычисление общей суммы товаров в корзине и их количества.

    Args:
        request (HttpRequest): объект запроса
    Returns:
        tuple: общая сумма товаров в корзине, количество товаров в корзине

    """
    user_basket = BasketItem.objects.filter(cart__user=request.user).select_related("product").aggregate(
        count=Sum("quantity"), total=Sum(F("product__price") * F("quantity"))
    )
    return (
        0 if user_basket.get("total", 0) is None else user_basket.get("total", 0),
        0 if user_basket.get("count", 0) is None else user_basket.get("count", 0)  # noqa: COM812
    )


def update_context_with_basket_data(request, context: dict) -> dict:  # noqa: ANN001
    """Добавление нужных данных в контекст view для отображения иконки корзины в тулбаре.

    Args:
        request (HttpRequest): объект запроса
        context (dict): контекст, передаваемый в шаблон
    Returns:
        контекст, обогащённый данными о состоянии корзины пользователя

    """  # noqa: RUF002
    if request.user.is_authenticated:
        total, count = calculate_basket_total(request)
        context.update({"items_count": count, "subtotal": total, "total": total,"delivery_price": 0 })
    return context


# TODO(ove): Это отдельная логика.  Куда-то нужно перенести из utils.
def _item_count_change(request, item_id: int, delta: int) -> tuple[BasketItem, bool]:  # noqa: ANN001
    """Изменение количества товара в корзине.

    Args:
        request (HttpRequest): объект запроса.
        item_id (int): id товара в корзине.
        delta (int): изменение количества товара
    Returns:
        ИфылуеItem: строка с товаром в корзине.
        bool : успешное изменение количества товара.

    """  # noqa: RUF002
    item = get_object_or_404(BasketItem, id=item_id, cart__user=request.user)
    quantity = item.quantity

    new_quantity = quantity + delta
    if delta > 0:
        if new_quantity > item.product.stock:
            messages.warning(request, "Недостаточное количество товара на складе!")
            return item, False
    elif new_quantity < 1:
        messages.info(request, 'Для удаления товара нажмите справа на кнопку "Удалить"')
        return item, False
    item.quantity = new_quantity
    item.save()
    return item, True
