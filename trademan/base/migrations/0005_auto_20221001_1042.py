# Generated by Django 2.2.19 on 2022-10-01 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_auto_20221001_1003'),
    ]

    operations = [
        migrations.AlterField(
            model_name='figi',
            name='api_trading_available',
            field=models.BooleanField(null=True, verbose_name='Можно торговать через API'),
        ),
    ]
