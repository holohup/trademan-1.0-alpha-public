# Generated by Django 2.2.19 on 2023-03-07 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0036_auto_20230305_2245'),
    ]

    operations = [
        migrations.AddField(
            model_name='figi',
            name='evening_trading',
            field=models.BooleanField(default=False, verbose_name='Вечерние торги'),
        ),
        migrations.AddField(
            model_name='figi',
            name='morning_trading',
            field=models.BooleanField(default=False, verbose_name='Утренние торги'),
        ),
    ]
