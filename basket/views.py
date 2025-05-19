import structlog  # noqa: D100, EXE002
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from basket.models import Basket, BasketItem
from basket.utils import _item_count_change, update_context_with_basket_data

logger = structlog.get_logger(__name__)


@login_required
@require_http_methods(["GET"])
def basket(request) -> HttpResponse:  # noqa: ANN001
    """Отображение корзины со списком товаров."""  # noqa: RUF002
    context = {
        "cart_items": BasketItem.objects.filter(cart__user=request.user).select_related("product").annotate(
            total_sum=F("product__price") * F("quantity")  # noqa: COM812
        ),
    }
    context = update_context_with_basket_data(request, context)
    return render(request, "basket.html", context=context)


@login_required
@require_http_methods(["POST"])
def create_item(request, product_id: int, quantity: int=1) -> HttpResponse:  # noqa: ANN001
    """Добавить товар в корзину.

    :param request: Параметры запроса.
    :param product_id: Идентификатор добавляемого в корзину покупателя товара.
    :param quantity: Количество добавляемого в корзину товара.
    :return:
    """
    basket, created = Basket.objects.get_or_create(user=request.user)
    item, created = BasketItem.objects.get_or_create(cart=basket, product_id=product_id)
    item.quantity = quantity
    item.save()
    return redirect("basket-list")


@login_required
@require_http_methods(["PATCH"])
def item_increment(request, item_id: int) -> HttpResponse:  # noqa: ANN001
    """Увеличение количества товара в корзине на единицу.

    Args:
        request (HttpRequest): объект запроса
        item_id (int): id товара в корзине

    """
    item, changed = _item_count_change(request, item_id, delta=1)
    context = {
        "cart_item": item,
        "row_update": True,
    }
    context = update_context_with_basket_data(request, context)
    return render(request, "partial/basket_item_row.html", context=context)


@login_required
@require_http_methods(["PATCH"])
def item_decrement(request, item_id: int) -> HttpResponse:  # noqa: ANN001
    """Уменьшение  количества товара в корзине на единицу.

    Args:
        request (HttpRequest): объект запроса
        item_id (int): id товара в корзине

    """
    item, changed = _item_count_change(request, item_id, delta=-1)
    context = {
        "cart_item": item,
        "row_update": True,
    }
    context = update_context_with_basket_data(request, context)
    return render(request, "partial/basket_item_row.html", context=context)


@login_required
@require_http_methods(["DELETE"])
def item_remove(request, item_id: int) -> HttpResponse:  # noqa: ANN001
    """Удалить товар из корзины.

    :param request: Параметры запроса.
    :param item_id: Идентификатор товара, удаляемого из корзины.
    :return:
    """
    item = get_object_or_404(BasketItem, id=item_id, cart__user=request.user)
    logger.info("Удаляем товар из корзины", товар=item.product.name)
    item.delete()
    if request.htmx:
        context = {
            "cart_item": item,
            "row_update": False,
        }
        context = update_context_with_basket_data(request, context)
        return render(request, "partial/basket_item_row.html", context=context)
    return redirect("basket-list")
