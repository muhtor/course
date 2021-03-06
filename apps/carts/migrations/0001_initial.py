# Generated by Django 3.0.2 on 2021-06-09 14:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('billing', '0001_initial'),
        ('courses', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('subtotal', models.DecimalField(decimal_places=3, default=0.0, max_digits=100)),
                ('total', models.DecimalField(decimal_places=3, default=0.0, max_digits=100)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['-created_at', '-updated_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CartCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('insert_type', models.CharField(choices=[('UNPAID', 'unpaid'), ('PAID', 'paid'), ('DESIRE', 'desire')], default='UNPAID', max_length=30)),
                ('quantity', models.PositiveSmallIntegerField(default=1)),
                ('paid', models.BooleanField(default=False)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='carts.Cart')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.Course')),
            ],
            options={
                'verbose_name': 'Cart Course',
                'verbose_name_plural': '     Cart Courses',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='cart',
            name='courses',
            field=models.ManyToManyField(blank=True, related_name='courses', through='carts.CartCourse', to='courses.Course'),
        ),
        migrations.AddField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cart',
            name='voucher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='billing.Voucher'),
        ),
    ]
