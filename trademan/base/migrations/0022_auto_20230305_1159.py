# Generated by Django 2.2.19 on 2023-03-05 08:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0021_auto_20230305_1024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spread',
            name='far_leg',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='f_spreads', to='base.Figi', verbose_name='Дальн. нога'),
        ),
        migrations.AlterField(
            model_name='spread',
            name='near_leg',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='n_spreads', to='base.Figi', verbose_name='Ближн. нога'),
        ),
        migrations.CreateModel(
            name='SpreadLegExecutionStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('executed', models.PositiveIntegerField(default=0, verbose_name='Исполнено шт.')),
                ('exec_price', models.DecimalField(decimal_places=10, default=0, max_digits=20, verbose_name='Ср. цена исполн.')),
                ('figi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Figi', verbose_name='Figi')),
                ('spread', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Spread', verbose_name='Spread')),
            ],
            options={
                'unique_together': {('figi', 'spread')},
            },
        ),
    ]
