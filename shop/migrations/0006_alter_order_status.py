# Generated by Django 5.1.7 on 2025-03-16 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_orderitem_product_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'В обработке'), ('completed', 'Завершён'), ('canceled', 'Отменён'), ('canceled_automatically', 'Автоматическая отмена')], default='pending', max_length=25, verbose_name='Статус'),
        ),
    ]
