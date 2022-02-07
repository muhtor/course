# Generated by Django 3.0.2 on 2021-06-09 14:29

import ckeditor.fields
import ckeditor_uploader.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(blank=True, max_length=255, unique=True)),
                ('path', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/category')),
                ('sort', models.CharField(blank=True, max_length=10)),
                ('parent_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='courses.Category')),
            ],
            options={
                'verbose_name_plural': '       Categories',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=100, verbose_name='Course name')),
                ('image', models.ImageField(upload_to='images/courses', verbose_name='Course Image')),
                ('description', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='Description')),
                ('paid', models.BooleanField(default=False)),
                ('author', models.CharField(max_length=64)),
                ('old_price', models.DecimalField(decimal_places=1, default=0.0, max_digits=10)),
                ('price', models.DecimalField(decimal_places=1, default=0.0, max_digits=10)),
                ('views', models.PositiveIntegerField(default=0)),
                ('person_count', models.PositiveIntegerField(default=0)),
                ('permission', models.BooleanField(default=True)),
                ('certificate', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='courses.Category', verbose_name='Category')),
            ],
            options={
                'verbose_name': 'Course',
                'verbose_name_plural': '     Courses',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=255, verbose_name='Lesson Name')),
                ('description', ckeditor.fields.RichTextField(verbose_name='Lesson Description')),
            ],
            options={
                'verbose_name': 'Lesson',
                'verbose_name_plural': 'Lessons',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='UploadFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='files/courses/lessons/audios')),
            ],
            options={
                'ordering': ['-created_at', '-updated_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserLesson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('new', 'New'), ('progress', 'Progress'), ('finished', 'Finished')], default='new', max_length=20, verbose_name='Process status')),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users_lessons', to='courses.Lesson')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User lesson',
                'verbose_name_plural': 'User lessons',
            },
        ),
        migrations.CreateModel(
            name='UserCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('status', models.CharField(choices=[('new', 'New'), ('progress', 'Progress'), ('finished', 'Finished')], default='new', max_length=20, verbose_name='Process status')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_courses', to='courses.Course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Course',
                'verbose_name_plural': 'User Courses',
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=100, verbose_name='Topic name')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topic_courses', to='courses.Course', verbose_name='Course')),
            ],
            options={
                'verbose_name': 'Topic',
                'verbose_name_plural': '    Topics',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='lesson',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lessons', to='courses.Topic', verbose_name='Topic'),
        ),
        migrations.CreateModel(
            name='CertificatedCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=100, verbose_name='Course name')),
                ('image', models.ImageField(upload_to='images/courses', verbose_name='Course Image')),
                ('description', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='Description')),
                ('paid', models.BooleanField(default=False)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='courses.Category', verbose_name='Category')),
                ('sub_courses', models.ManyToManyField(related_name='certificated_courses', to='courses.Course', verbose_name='Sub courses')),
            ],
            options={
                'verbose_name': 'Certificated course',
                'verbose_name_plural': 'Certificated courses',
            },
        ),
        migrations.CreateModel(
            name='CourseCertificate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash', models.CharField(blank=True, max_length=150, null=True, verbose_name='Hash for verify')),
                ('pdf', models.FileField(blank=True, null=True, upload_to='files/courses/certificates/', verbose_name='PDF file')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('qr', models.ImageField(blank=True, null=True, upload_to='images/courses/certificates/', verbose_name='QR code (link to the certificate)')),
                ('certificated_course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='certificates', to='courses.CertificatedCourse')),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='certificates', to='courses.Course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='certificates', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Course certificate',
                'verbose_name_plural': 'Courses certificates',
                'unique_together': {('user', 'course')},
            },
        ),
    ]
