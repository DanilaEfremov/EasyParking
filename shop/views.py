from smtplib import SMTPException
import json

from django.core.mail import EmailMessage
from django.db.models.aggregates import Sum
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, F
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils.timezone import now
from django.core.paginator import Paginator
import structlog

from .models import Product, Cart, CartItem, Order, OrderItem, ProductImage
from .forms import OrderForm


logger = structlog.get_logger(__name__)

def products(request):
    """Страница с товарами."""
    template = 'partials/products.html' if request.htmx else 'products/products.html'
    query = request.GET.get('q', None)
    sort_by = request.GET.get('sort_by', 'name')
    order = request.GET.get('order', 'asc')

    items = (Product.objects
             .filter(show_in_catalog=True)
             .order_by(f'-{sort_by}' if order == 'desc' else sort_by)
             # .values("id", "name", "description", "image", "price", "stock")
             )
    if query:
        items = items.filter(Q(name__icontains=query) | Q(description__icontains=query))
    paginator = Paginator(items, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'query': query,
        'sort_by': sort_by,
        'order': order,
    }
    if request.user.is_authenticated:
        total, count = calculate_cart_total(request)
        context.update({
            'items_count': count,
            'subtotal': total,
            'delivery_price': 0,
        })
    return render(request, template_name=template, context=context)


def product_detail(request, product_id, quantity=1):
    """Страница с деталями товара."""
    product = get_object_or_404(Product, id=product_id)
    additional_images = product.additional_images.all()
    filtered_items = Product.objects.filter(show_in_catalog=True).exclude(id=product_id).order_by('?')[:4]
    context = {
        'product': product,
        'quantity': quantity,
        'additional_images': additional_images,
        'filtered_items': filtered_items,
    }
    if request.user.is_authenticated:
        total, count = calculate_cart_total(request)
        context.update({
            'items_count': count,
            'subtotal': total,
            'delivery_price': 0,
        })
    return render(request, 'products/product_detail.html', context=context)


@login_required
def add_to_cart(request, product_id):
    """Добавить товар в корзину."""
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    quantity = int(request.GET.get("quantity", 1))
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity = quantity
    cart_item.save()
    return redirect('cart')


@login_required
def cart(request):
    """Отображение корзины."""
    total, count = calculate_cart_total(request)
    cart_items = (CartItem.objects
                  .filter(cart__user=request.user)
                  .select_related('product')
                  .annotate(total_sum=F('product__price') * F('quantity'))
                  )

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        new_quantity = int(request.POST.get('quantity', 1))
        cart_item = get_object_or_404(CartItem, id=item_id)
        if new_quantity > cart_item.product.stock:
            return JsonResponse({"error": "Недостаточно товаров на складе"}, status=400)
        cart_item.quantity = new_quantity
        cart_item.save()
        return redirect('cart')

    context = {
        'items_count': count,
        'subtotal': total,
        'delivery_price': 0,
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'cart/cart.html', context=context)


@login_required
def remove_from_cart(request, product_id):
    """Удалить товар из корзины."""
    item = get_object_or_404(CartItem, id=product_id, cart__user=request.user)
    item.delete()
    if request.htmx:
        total, count = calculate_cart_total(request)
        context = {
            'cart_item': item,
            'delivery_price': 0,
            'total': total,
            'items_count': count,
            'row_update': False
        }
        return render(request, 'cart/parcial/cart_row.html', context=context)
    else:
        return redirect('cart')


@login_required
def checkout(request):
    """Оформление заказа."""
    total, count = calculate_cart_total(request)
    user = request.user

    context = {
        'items_count': count,
        'subtotal': total,
        'delivery_price': 0,
        'cart_items': None,
        'total': total,
    }
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            cart_items = CartItem.objects.filter(cart__user=user).select_related('product').annotate(
                total_sum=F('product__price') * F('quantity'))
            context['form'] = form
            context['cart_items'] = cart_items
            request.session['form'] = form.cleaned_data
            return render(request, 'cart/review.html', context)
    else:
        form = OrderForm(instance=user)  # Авто-заполнение
    context['form'] = form
    return render(request, 'cart/checkout.html', context=context)


@login_required
def checkout_final(request):
    data = request.session.pop('form', None)
    if not data:
        logger.info("No form data found in session, redirecting to home")
        return redirect('home')

    email = data.get('email', '')
    full_name = data.get('full_name', '')
    address = data.get('address', '')
    city = data.get('city', '')
    zip_code = data.get('zip_code', '')
    recipient = data.get('recipient', '')
    comment = data.get('comment', '')

    total, count = calculate_cart_total(request)

    try:
        with (transaction.atomic()):
            cart_items = CartItem.objects.filter(cart__user=request.user).select_related('product').select_for_update(of=('product',))
            # .annotate(
            #     total_sum=F('product__price') * F('quantity')
            # )
            items_to_delete = []
            for item in cart_items:
                if item.quantity <= item.product.stock:
                    item.product.stock -= item.quantity
                    items_to_delete.append(item.product)
                else:
                    raise Exception("Недостаточно товаров на складе!")
            Product.objects.bulk_update(items_to_delete, ['stock'])

            order = Order.objects.create(
                user=request.user,
                total_price=total,
                created_at=now(),
                email=email,
                full_name=full_name,
                address = address,
                city = city,
                zip_code = zip_code,
                recipient = recipient,
                comment = comment
            )

            order_items = [
                #TODO:  Сделать инициализацию от cart_items: __init__(self, order, cart_item)
                OrderItem(
                    order=order,
                    product_id=item.product.id,
                    name=item.product.name,
                    description=item.product.description,
                    quantity=item.quantity,
                    price=item.product.price
                ) for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)
            cart_items.delete()

    except Exception:
        logger.error(f"Order creation failed", exc_info=True)
        return render(request, 'cart/checkout_failed.html', context = {'items_count': count, 'subtotal': total, 'delivery_price': 0,})

    # Формирование деталей заказа
    salutation = 'Уважаемый' if request.user.profile.gender == 'M' else 'Уважаемая'
    order_details = (
            f"{salutation} {full_name} ({request.user.username}), ваш заказ номер  {order.id} оформлен!\n\n"
            f"Адрес доставки: город {city}, {address}, индекс: {zip_code}\n\n"
            f"Получатель вашего заказа: {recipient}\n\n"
            "Позиции:\n"
    )

    order_details += "\n".join([f"- {item.name} x {item.quantity}" for item in order_items])
    order_details += f"\n\nОбщая сумма: {total:.2f} руб."
    if comment:
        order_details += f"\n\nКомментарий к заказу: {comment}."
    # Отправка письма
    email_to_send = EmailMessage(
        subject="Подтверждение заказа",
        body=order_details,
        from_email="easyparking673@gmail.com",
        to=[email],
        bcc=["easyparking673@gmail.com"],
    )
    try:
        email_to_send.send(fail_silently=False)
    except SMTPException as e:
        logger.warning(f"Ошибка при отправке письма: {e}")

    context = {
        'items_count': 0,
        'subtotal': 0,
        'delivery_price': 0,
    }
    logger.info('Order created successfully!')

    return render(request, 'cart/checkout_success.html', context=context)


@login_required
def update_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    if request.method == "POST":
        data = json.loads(request.body)
        item_id = data.get("item_id")
        quantity = int(data.get("quantity"))

        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        if 1 <= quantity <= cart_item.product.stock:
            cart_item.quantity = quantity
            cart_item.save()

            total = sum(
                item.quantity * item.product.price for item in cart.items.all()
            )

            return JsonResponse({"success": True, "new_total": total})
        else:
            return JsonResponse({"success": False, "error": "Некорректное количество."})


def _item_count_change(request, item_id: int, delta: int) -> (CartItem, bool):
    """Изменение количества товара в корзине

    Args:
        request:(HttpRequest): объект запроса
        item_id (int): id товара в корзине
        delta (int): изменение количества товара

    Returns:
        bool: успешное изменение количества товара"""
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = item.quantity
    new_quantity = quantity + delta
    if delta > 0:
        if new_quantity > item.product.stock:
            messages.warning(request, 'Недостаточно товаров на складе!')
            return item, False
    else:
        if new_quantity < 1:
            messages.info(request, 'Для удаления товара нажмите справа на кнопку "Удалить"')
            return item, False
    item.quantity = new_quantity
    item.save()
    return item, True


def calculate_cart_total(request) -> (int, int):
    """Вычисление общей суммы товаров в корзине и их количества
    Args:
        request (HttpRequest): объект запроса
    Returns:
        tuple: общая сумма товаров в корзине, количество товаров в корзине"""

    cart = CartItem.objects.filter(cart__user=request.user).select_related('product').aggregate(count=Sum('quantity'), total=Sum(F('product__price') * F('quantity')))
    return cart.get('total', -10), cart.get('count', -20)


@login_required
@require_http_methods(["PATCH"])
def item_increment(request, item_id: int):
    """Увеличение количества товара в корзине на единицу.

    Args:
        request (HttpRequest): объект запроса
        item_id (int): id товара в корзине
    """
    item, changed = _item_count_change(request, item_id, delta=1)
    total, count = calculate_cart_total(request)
    context = {
        'cart_item': item,
        'delivery_price': 0,
        'total': total,
        'items_count': count,
        'row_update': True
    }
    # logger.warning(f"Cart context: {context}")
    return render(request, 'cart/parcial/cart_row.html', context=context)


@login_required
@require_http_methods(["PATCH"])
def item_decrement(request, item_id: int):
    """Уменьшение  количества товара в корзине на единицу.

       Args:
           request (HttpRequest): объект запроса
           item_id (int): id товара в корзине
       """
    item, changed = _item_count_change(request, item_id, delta=-1)
    total, count = calculate_cart_total(request)
    context = {
        'cart_item': item,
        'delivery_price': 0,
        'total': total,
        'items_count': count,
        'row_update': True
    }
    return render(request, 'cart/parcial/cart_row.html', context=context)


def product_increment(request, product_id: int, quantity: int):
    product = get_object_or_404(Product, id=product_id)
    max = product.stock
    if quantity < max:
        quantity += 1
    else:
        messages.warning(request, 'Недостаточно товаров на складе!')
    if request.htmx:
        template = 'partials/product_quantity.html'
        context = {'quantity': quantity, 'product': product,}
    else:
        additional_images = product.additional_images.all()
        all = Product.objects.all()
        filtered_items = [item for item in all if item.id != product_id][:4]
        context = {
            'title': product.name,
            'product': product,
            'quantity': quantity,
            'additional_images': additional_images,
            'filtered_items': filtered_items
        }
        template = 'products/product_detail.html'
    return render(request, template_name=template, context=context)


def product_decrement(request, product_id: int, quantity: int):
    product = get_object_or_404(Product, id=product_id)
    if quantity > 1:
        quantity -=1
    if request.htmx:
        template = 'partials/product_quantity.html'
        context = {'quantity': quantity, 'product': product, }
    else:
        additional_images = product.additional_images.all()
        all = Product.objects.all()
        filtered_items = [item for item in all if item.id != product_id][:4]
        context = {
            'title': product.name,
            'product': product,
            'quantity': quantity,
            'additional_images': additional_images,
            'filtered_items': filtered_items
        }
        template = 'products/product_detail.html'
    return render(request, template_name=template, context=context)