# Generated by Django 2.2.19 on 2022-09-29 05:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stops',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('white_list', models.BooleanField(default=False)),
                ('black_list', models.BooleanField(default=False)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.Figi', verbose_name='Акция')),
            ],
            options={
                'verbose_name': 'Стоп',
                'verbose_name_plural': 'Стопы',
            },
        ),
    ]
