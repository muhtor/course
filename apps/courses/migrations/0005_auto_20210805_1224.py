# Generated by Django 3.0.2 on 2021-08-05 12:24

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_auto_20210802_1229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='certificatedcourse',
            name='discount_percent',
            field=models.SmallIntegerField(default=0, help_text='The certificated course price is the sub courses price with the discount percent. Works if a user did not paid for any of the sub courses', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Discount price percent'),
        ),
    ]