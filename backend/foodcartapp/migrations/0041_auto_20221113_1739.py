# Generated by Django 3.2.15 on 2022-11-13 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, verbose_name='Комментарий'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('New', 'Новый'), ('Clarified', 'Уточнён'), ('Packed', 'Собран'), ('Delivered', 'Доставлен')], db_index=True, default='New', max_length=10, verbose_name='Статус'),
        ),
    ]
