# Generated by Django 2.2.19 on 2023-03-05 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0035_auto_20230305_2237'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nearspreadleg',
            name='figi',
        ),
        migrations.RemoveField(
            model_name='nearspreadleg',
            name='spread',
        ),
        migrations.AddField(
            model_name='figi',
            name='basic_asset',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Базовый актив'),
        ),
        migrations.DeleteModel(
            name='FarSpreadLeg',
        ),
        migrations.DeleteModel(
            name='NearSpreadLeg',
        ),
    ]
