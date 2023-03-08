# Generated by Django 2.2.19 on 2023-03-08 08:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0037_auto_20230307_1435'),
    ]

    operations = [
        migrations.RenameField(
            model_name='figi',
            old_name='type',
            new_name='asset_type',
        ),
        migrations.AlterUniqueTogether(
            name='figi',
            unique_together={('ticker', 'asset_type')},
        ),
    ]
