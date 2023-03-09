# Generated by Django 2.2.19 on 2023-03-05 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0020_auto_20230305_1015'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='spread',
            name='asset',
        ),
        migrations.AlterField(
            model_name='spread',
            name='ratio',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Far leg / near leg even ratio'),
        ),
    ]