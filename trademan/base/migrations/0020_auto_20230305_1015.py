# Generated by Django 2.2.19 on 2023-03-05 07:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0019_auto_20230305_1001'),
    ]

    operations = [
        migrations.AddField(
            model_name='spread',
            name='far_leg',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='far_leg', to='base.Figi', verbose_name='Дальн. нога'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='spread',
            name='ratio',
            field=models.PositiveSmallIntegerField(default=100, verbose_name='Far leg / near leg even ratio'),
        ),
        migrations.AlterField(
            model_name='spread',
            name='asset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='spread', to='base.Figi', verbose_name='Актив'),
        ),
    ]
