# Generated by Django 2.2.19 on 2022-10-10 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0015_delete_bonds'),
    ]

    operations = [
        migrations.AlterField(
            model_name='figi',
            name='type',
            field=models.CharField(choices=[('S', 'Stock'), ('F', 'Future')], max_length=1, verbose_name='Акция или фьючерс'),
        ),
    ]
