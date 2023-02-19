# Generated by Django 2.2.19 on 2022-10-01 14:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_auto_20221001_1055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='figi',
            name='api_trading_available',
            field=models.BooleanField(verbose_name='API'),
        ),
        migrations.AlterField(
            model_name='figi',
            name='buy_enabled',
            field=models.BooleanField(verbose_name='Buy'),
        ),
        migrations.AlterField(
            model_name='figi',
            name='min_price_increment',
            field=models.DecimalField(decimal_places=10, max_digits=20, verbose_name='Шаг цены'),
        ),
        migrations.AlterField(
            model_name='figi',
            name='sell_enabled',
            field=models.BooleanField(verbose_name='Sell'),
        ),
        migrations.AlterField(
            model_name='figi',
            name='short_enabled',
            field=models.BooleanField(verbose_name='Short'),
        ),
        migrations.AlterField(
            model_name='restorestops',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Активная заявка?'),
        ),
        migrations.AlterField(
            model_name='restorestops',
            name='asset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='restorestops', to='base.Figi', verbose_name='Актив'),
        ),
        migrations.AlterField(
            model_name='sellbuy',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Активная заявка?'),
        ),
        migrations.AlterField(
            model_name='sellbuy',
            name='asset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sellbuy', to='base.Figi', verbose_name='Актив'),
        ),
        migrations.AlterField(
            model_name='spread',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Активная заявка?'),
        ),
        migrations.AlterField(
            model_name='spread',
            name='asset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='spread', to='base.Figi', verbose_name='Дальняя нога'),
        ),
        migrations.AlterField(
            model_name='stops',
            name='stock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stops', to='base.Figi', verbose_name='Акция'),
        ),
    ]
