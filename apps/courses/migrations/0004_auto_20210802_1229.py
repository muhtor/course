# Generated by Django 3.0.2 on 2021-08-02 12:29

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_certificatedcourse_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='certificatedcourse',
            name='price',
        ),
        migrations.AddField(
            model_name='certificatedcourse',
            name='discount_percent',
            field=models.SmallIntegerField(default=0, help_text='The certificated course price is the sub courses price with the discount percent', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Discount price percent'),
        ),
    ]
