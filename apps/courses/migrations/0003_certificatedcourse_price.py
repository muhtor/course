# Generated by Django 3.0.2 on 2021-07-28 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_auto_20210609_1444'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificatedcourse',
            name='price',
            field=models.DecimalField(decimal_places=1, default=0.0, max_digits=10),
        ),
    ]