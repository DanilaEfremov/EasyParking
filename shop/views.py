import structlog  # noqa: D100, EXE002
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from basket.utils import update_context_with_basket_data

from .models import Product

logger = structlog.get_logger(__name__)


@require_http_methods(["GET"])
def products(request) -> HttpResponse:  # noqa: ANN001
    """Страница с товарами."""  # noqa: RUF002
    template = "partial/products.html" if request.htmx else "products.html"
    query = request.GET.get("q", None)
    sort_by = request.GET.get("sort_by", "name")
    order = request.GET.get("order", "asc")

    items = (Product.objects
             .filter(show_in_catalog=True)
             .order_by(f"-{sort_by}" if order == "desc" else sort_by)
             # .values("id", "name", "description", "image", "price", "stock")
             )
    if query:
        items = items.filter(Q(name__icontains=query) | Q(description__icontains=query))
    paginator = Paginator(items, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "query": query,
        "sort_by": sort_by,
        "order": order,
    }
    return render(request, template_name=template, context=update_context_with_basket_data(request, context))


@require_http_methods(["GET"])
def product_detail(request, product_id: int, quantity: int=1) -> HttpResponse:  # noqa: ANN001
    """Страница с деталями товара.

    :param request: Параметры запроса
    :param product_id: id товара, подробную информацию о котором необходимо отобразить
    :param quantity: Количество товара
    :return:
    """  # noqa: RUF002
    product = get_object_or_404(Product, id=product_id)
    additional_images = product.additional_images.all()
    filtered_items = Product.objects.filter(show_in_catalog=True).exclude(id=product_id).order_by('?')[:4]
    context = {
        "product": product,
        "quantity": quantity,
        "additional_images": additional_images,
        "filtered_items": filtered_items,
    }
    return render(request, "product_detail.html", context=update_context_with_basket_data(request, context))


@require_http_methods(["PATCH"])
def product_increment(request, product_id: int, quantity: int) -> HttpResponse:  # noqa: ANN001
    """Увеличение количества товара на странице с детальным описанием.

    :param request: Параметры запроса
    :param product_id: id товара, количество которого планируется увеличить на единицу
    :param quantity: Текущее количество товара
    :return:
    """
    product = get_object_or_404(Product, id=product_id)
    if quantity < product.stock:
        quantity += 1
    else:
        messages.warning(request, "Недостаточно товаров на складе!")
    if request.htmx:
        template = "partial/product_quantity_htmx.html"
        context = {"quantity": quantity, "product": product}
    else:
        additional_images = product.additional_images.all()
        filtered_items = Product.objects.filter(show_in_catalog=True).exclude(id=product_id).order_by("?")[:4]
        context = {
            "title": product.name,
            "product": product,
            "quantity": quantity,
            "additional_images": additional_images,
            "filtered_items": filtered_items,
        }
        context = update_context_with_basket_data(request, context)
        template = "product_detail.html"
    return render(request, template_name=template, context=context)


@require_http_methods(["PATCH"])
def product_decrement(request, product_id: int, quantity: int) -> HttpResponse:  # noqa: ANN001
    """Уменьшение количества товара на странице с детальным описанием.

    :param request: Параметры запроса
    :param product_id: id товара, количество которого планируется уменьшить на единицу
    :param quantity: Текущее количество товара
    :return:
    """
    product = get_object_or_404(Product, id=product_id)
    if quantity == 1:
        return HttpResponse(status=204)
    if quantity > 1:
        quantity -=1
    if request.htmx:
        template = "partial/product_quantity_htmx.html"
        context = {"quantity": quantity, "product": product, }
    else:
        additional_images = product.additional_images.all()
        filtered_items = Product.objects.filter(show_in_catalog=True).exclude(id=product_id).order_by("?")[:4]
        context = {
            "title": product.name,
            "product": product,
            "quantity": quantity,
            "additional_images": additional_images,
            "filtered_items": filtered_items,
        }
        context = update_context_with_basket_data(request, context)
        template = "product_detail.html"
    return render(request, template_name=template, context=context)
