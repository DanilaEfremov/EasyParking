from smtplib import SMTPException  # noqa: D100, EXE002

import structlog
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.db import transaction
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.timezone import now

from basket.models import BasketItem
from basket.utils import calculate_basket_total
from order.forms import OrderForm
from order.models import Order, OrderItem
from shop.models import Product

logger = structlog.get_logger(__name__)


@login_required
def checkout(request) -> HttpResponse:  # noqa: ANN001
    """Оформление заказа."""
    total, count = calculate_basket_total(request)
    user = request.user
    context = {
        "items_count": count,
        "subtotal": total,
        "delivery_price": 0,
        "cart_items": None,
        "total": total,
    }
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            cart_items = BasketItem.objects.filter(cart__user=user).select_related("product").annotate(
                total_sum=F("product__price") * F("quantity")
            )
            context["form"] = form
            context["cart_items"] = cart_items
            request.session["form"] = form.cleaned_data
            return render(request, "review.html", context)
    else:
        form = OrderForm(instance=user)  # Авто-заполнение
    context["form"] = form
    return render(request, "checkout.html", context=context)


@login_required
def checkout_final(request) -> HttpResponse:  # noqa: ANN001
    """???."""
    data = request.session.pop("form", None)
    if not data:
        logger.info("No form data found in session, redirecting to home")
        return redirect("home")
    email = data.get("email", "")
    full_name = data.get("full_name", "")
    address = data.get("address", "")
    city = data.get("city", "")
    zip_code = data.get("zip_code", "")
    recipient = data.get("recipient", "")
    comment = data.get("comment", "")
    total, count = calculate_basket_total(request)
    try:
        with (transaction.atomic()):
            cart_items = BasketItem.objects.filter(
                cart__user=request.user  # noqa: COM812
            ).select_related("product").select_for_update(of=("product",))
            items_to_delete = []
            for item in cart_items:
                if item.quantity <= item.product.stock:
                    item.product.stock -= item.quantity
                    items_to_delete.append(item.product)
                else:
                    msg = "Недостаточно товаров на складе!"
                    raise Exception(msg)  # noqa: TRY002, TRY301
            Product.objects.bulk_update(items_to_delete, ["stock"])

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
                comment = comment,
            )

            order_items = [
                #TODO:  Сделать инициализацию от cart_items: __init__(self, order, cart_item)
                OrderItem(
                    order=order,
                    product_id=item.product.id,
                    name=item.product.name,
                    description=item.product.description,
                    quantity=item.quantity,
                    price=item.product.price,
                ) for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)
            cart_items.delete()
    except Exception:
        logger.error("Order creation failed", exc_info=True)  # noqa: G201
        return render(
            request,
            "checkout_failed.html",
            context = {"items_count": count, "subtotal": total, "delivery_price": 0},
        )

    # Формирование деталей заказа
    salutation = "Уважаемый" if request.user.profile.gender == "M" else "Уважаемая"
    order_details = (
            f"{salutation} {full_name} ({request.user.username}), ваш заказ номер  {order.id} оформлен!\n\n"
            f"Адрес доставки: город {city}, {address}, индекс: {zip_code}\n\n"
            f"Получатель вашего заказа: {recipient}\n\n"
            "Позиции:\n"
    )

    order_details += "\n".join([f"- {item.name} x {item.quantity}" for item in order_items])
    order_details += f"\n\nОбщая сумма: {total:.2f} руб."  # noqa: RUF001
    if comment:
        order_details += f"\n\nКомментарий к заказу: {comment}."  # noqa: RUF001
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
        logger.warning("Ошибка при отправке письма.", exc_info=e)
    context = {
        "items_count": 0,
        "subtotal": 0,
        "delivery_price": 0,
    }
    logger.info("Order created successfully!")
    return render(request, "checkout_success.html", context=context)

