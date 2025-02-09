# Generated by Django 5.1.2 on 2024-11-11 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='market',
            index=models.Index(fields=['symbol'], name='trading_mar_symbol_e3036d_idx'),
        ),
        migrations.AddIndex(
            model_name='market',
            index=models.Index(fields=['timestamp'], name='trading_mar_timesta_f2879e_idx'),
        ),
        migrations.AddIndex(
            model_name='market',
            index=models.Index(fields=['symbol', 'timestamp'], name='trading_mar_symbol_958495_idx'),
        ),
    ]
