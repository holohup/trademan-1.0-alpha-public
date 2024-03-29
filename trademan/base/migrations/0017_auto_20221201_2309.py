# Generated by Django 2.2.19 on 2022-12-01 20:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0016_auto_20221010_1034'),
    ]

    operations = [
        migrations.AddField(
            model_name='spread',
            name='exec_price',
            field=models.FloatField(default=0, verbose_name='Ср. цена исполн.'),
        ),
        migrations.AlterField(
            model_name='restorestops',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Активно?'),
        ),
        migrations.AlterField(
            model_name='restorestops',
            name='executed',
            field=models.PositiveIntegerField(default=0, verbose_name='Исполнено'),
        ),
        migrations.AlterField(
            model_name='sellbuy',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Активно?'),
        ),
        migrations.AlterField(
            model_name='sellbuy',
            name='executed',
            field=models.PositiveIntegerField(default=0, verbose_name='Исполнено'),
        ),
        migrations.AlterField(
            model_name='spread',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Активно?'),
        ),
        migrations.AlterField(
            model_name='spread',
            name='asset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='spread', to='base.Figi', verbose_name='Дальн. нога'),
        ),
        migrations.AlterField(
            model_name='spread',
            name='executed',
            field=models.PositiveIntegerField(default=0, verbose_name='Исполнено'),
        ),
        migrations.AlterField(
            model_name='spread',
            name='near_leg',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='near_leg', to='base.Figi', verbose_name='Ближн. нога'),
        ),
    ]
