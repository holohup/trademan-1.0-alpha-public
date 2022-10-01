# Generated by Django 2.2.19 on 2022-10-01 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_auto_20221001_1042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='figi',
            name='api_trading_available',
            field=models.BooleanField(default=False, verbose_name='Можно торговать через API'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='figi',
            name='buy_enabled',
            field=models.BooleanField(default=False, verbose_name='Можно покупать'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='figi',
            name='sell_enabled',
            field=models.BooleanField(default=False, verbose_name='Можно продавать'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='figi',
            name='short_enabled',
            field=models.BooleanField(default=False, verbose_name='Можно шортить'),
            preserve_default=False,
        ),
    ]
