# Generated by Django 3.0.2 on 2021-07-07 06:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20210702_0925'),
        ('billing', '0009_auto_20210702_0925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.Order'),
        ),
    ]