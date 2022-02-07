# Generated by Django 3.0.2 on 2021-07-01 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0004_auto_20210701_0541'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='paycom_time',
        ),
        migrations.AddField(
            model_name='transaction',
            name='time_millisecond',
            field=models.CharField(blank=True, max_length=255, verbose_name='API kelgan millisecond vaqt'),
        ),
    ]
