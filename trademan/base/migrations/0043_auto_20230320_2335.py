# Generated by Django 2.2.19 on 2023-03-20 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0042_auto_20230320_2331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sellbuy',
            name='amount',
            field=models.PositiveIntegerField(default=0, verbose_name='Количество к исполнению'),
        ),
        migrations.AlterField(
            model_name='stoporders',
            name='amount',
            field=models.PositiveIntegerField(default=0, verbose_name='Количество к исполнению'),
        ),
    ]
