# Generated by Django 2.2.19 on 2023-03-05 19:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0033_auto_20230305_2203'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpreadStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('far_leg_executed', models.PositiveIntegerField(default=0, verbose_name='Far leg executed')),
                ('near_leg_executed', models.PositiveIntegerField(default=0, verbose_name='Near leg executed')),
                ('far_leg_avg_price', models.DecimalField(decimal_places=10, default=0, max_digits=20, verbose_name='Avg far leg execution price')),
                ('near_leg_avg_price', models.DecimalField(decimal_places=10, default=0, max_digits=20, verbose_name='Avg near leg execution price')),
            ],
        ),
        migrations.AlterField(
            model_name='spread',
            name='far_leg',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='far_spreads', to='base.Figi', verbose_name='Дальн. нога'),
        ),
        migrations.AlterField(
            model_name='spread',
            name='near_leg',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='near_spreads', to='base.Figi', verbose_name='Ближн. нога'),
        ),
        migrations.AddField(
            model_name='spread',
            name='stats',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='spreads', to='base.SpreadStats', verbose_name='Execution stats'),
            preserve_default=False,
        ),
    ]