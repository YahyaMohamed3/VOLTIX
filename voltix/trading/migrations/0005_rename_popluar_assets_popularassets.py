# Generated by Django 5.1.2 on 2024-12-07 20:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0004_popluar_assets_delete_liveprice_delete_market'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='popluar_assets',
            new_name='PopularAssets',
        ),
    ]
