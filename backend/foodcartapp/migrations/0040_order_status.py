# Generated by Django 3.2.15 on 2022-11-13 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0039_auto_20221112_2355'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('New', 'Новый'), ('Clarified', 'Уточнён'), ('Packed', 'Собран'), ('Delivered', 'Доставлен')], db_index=True, default='NEW', max_length=10, verbose_name='Статус'),
        ),
    ]
