# Generated by Django 3.0.2 on 2021-08-01 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_certificatedcourse_price'),
        ('carts', '0002_auto_20210801_1249'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='certificated_courses',
            field=models.ManyToManyField(blank=True, related_name='courses', through='carts.CartCourse', to='courses.CertificatedCourse'),
        ),
    ]
