# Generated by Django 2.2.19 on 2023-03-05 10:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0023_auto_20230305_1328'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assetstats',
            options={'verbose_name': 'Статистика по активу', 'verbose_name_plural': 'Статистика по активу'},
        ),
        migrations.AlterField(
            model_name='spread',
            name='far_leg',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='spreads', to='base.AssetStats', verbose_name='Дальн. нога'),
        ),
        migrations.AlterField(
            model_name='spread',
            name='near_leg',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='spreads', to='base.Figi', verbose_name='Ближн. нога'),
        ),
    ]
