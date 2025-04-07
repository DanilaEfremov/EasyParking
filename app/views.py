from smtplib import SMTPException

from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render, redirect

from shop.views import calculate_cart_total
import structlog

logger = structlog.get_logger(__name__)

def about(request):
    """Страница 'О себе'."""
    if request.user.is_authenticated:
        total, count = calculate_cart_total(request)
        context = {
            'items_count': count,
            'subtotal': total,
            'delivery_price': 0,
        }
    else:
        context = {}
    return render(request, 'about.html', context=context)


def contacts(request):
    """Страница 'Контакты'."""
    if request.user.is_authenticated:
        total, count = calculate_cart_total(request)
        context = {
            'items_count': count,
            'subtotal': total,
            'delivery_price': 0,
        }
    else:
        context = {}
    return render(request, 'contact-us.html', context=context)

def send_email(request):
    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        email = request.POST.get('email', '').strip()
        name = request.POST.get('name', '').strip()
        details = f'Cоздано новое обращение! \n \nИмя: {name} \nПочта: {email} \nСообщение: {message}'

        if not message:
            return HttpResponse('Сообщение не может быть пустым!', status=400)

        email = EmailMessage(
            subject="Создано обращение",
            body=details,
            from_email="easyparking673@gmail.com",
            to=["easyparking673@gmail.com", ],
        )
        try:
            email.send(fail_silently=False)
            logger.info('Email sent successfully')
            return redirect('home')
        except SMTPException as e:
            logger.error('Error sending email', exc_info=e)
            print(f"Ошибка при отправке электронного письма: {e}")