# Generated by Django 2.2.19 on 2023-03-05 17:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0029_auto_20230305_2017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nearspreadleg',
            name='figi',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='near_leg', to='base.Figi', verbose_name='Figi'),
        ),
    ]