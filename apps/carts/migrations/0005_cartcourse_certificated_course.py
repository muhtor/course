# Generated by Django 3.0.2 on 2021-08-05 12:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_auto_20210805_1224'),
        ('carts', '0004_auto_20210802_1229'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartcourse',
            name='certificated_course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='courses.CertificatedCourse'),
        ),
    ]