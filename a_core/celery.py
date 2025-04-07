import os
import logging

from celery import Celery
from celery import shared_task
from celery.backends.database import retry
from celery.schedules import crontab

logger = logging.getLogger(__name__)

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'a_core.settings')

app = Celery('a_core')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')
#
#     sender.add_periodic_task(30.0, test.s('hello'), name='add every 30')
#
#     sender.add_periodic_task(30.0, test.s('world'), expires=10)
#
#     sender.add_periodic_task(
#         crontab(hour=7, minute=30, day_of_week=1),
#         test.s('Happy Mondays!'),
#     )
#


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


@app.task(bind=False, ignore_result=True, name='Автоматическая отмена заказа', )
def set_automatically_canceled(order_id, status):
    from shop.models import Order
    try:
        order = Order.objects.get(id=order_id)
        if order.status == 'pending':
            order.status = status
            order.save()
    except Order.DoesNotExist:
        logger.error(f"Заказ {order_id} не существует для отмены.")


@app.task(bind=False, ignore_result=True, name='Проверка заказов', )
def my_task():
    from shop.models import Order
    from constance import config
    from django.utils import timezone
    from datetime import timedelta
    from smtplib import SMTPException
    from django.core.mail import EmailMessage

    cancel_time = config.TIME_TO_CANCEL_ORDER + 4 * 60 * 60 * 24
    # cancel_time = 3 * 60
    two_weeks_ago = timezone.now() - timedelta(seconds=cancel_time)
    order_ids = Order.objects.filter(status='pending', created_at__lte=two_weeks_ago).values_list("id", flat=True)

    for order_id in order_ids:
        logger.info(f"Заказ {order_id} замечен")

    if order_ids:
        details = '\n'.join([f"Заказ {order_id}" for order_id in order_ids])
        details += '\n\n'
        details += 'Эти заказы не отменились автоматически. Проверьте их'

        email = EmailMessage(
            subject="Некоторые заказы не отменились автоматически. Проверьте их",
            body=details,
            from_email="easyparking673@gmail.com",
            to=["easyparking673@gmail.com", ],
        )
        try:
            email.send(fail_silently=False)
            logger.info('Почта отправлена (периодическая проверка статуса заказа)')
        except SMTPException as e:
            logger.error('Ошибка отправки почты (периодическая проверка статуса заказа)', exc_info=e)

        chunk_size = 10
        for count, i in enumerate(range(0, len(order_ids), chunk_size)):
            chunk = order_ids[i:i + chunk_size]
            cancel_orders_task.apply_async(args=[chunk], countdown=count * 5 * 60)


@app.task(bind=False, ignore_result=True, name='Отмена заказов')
def cancel_orders_task(order_ids):
    for order_id in order_ids:
        set_automatically_canceled(order_id, 'canceled_automatically')

    # from shop.models import Order
    #
    # orders = Order.objects.filter(id__in=order_ids)
    # for order in orders:
    #     order.status = 'canceled_automatically'
    #     order.save()
    #     logger.info(f"Заказ {order.id} отменен")