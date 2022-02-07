from django.contrib import admin
from django import forms
from .models import *
from nested_admin.nested import NestedModelAdmin, NestedTabularInline
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class LessonInline(NestedTabularInline):
    model = Lesson
    extra = 0


class TopicInline(NestedTabularInline):
    model = Topic
    inlines = [LessonInline, ]
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'id', 'parent_category_id', 'parent_category', 'path', 'sort', 'is_active')
    list_per_page = 15


class CourseAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Course
        fields = '__all__'


@admin.register(Course)
class CourseAdmin(NestedModelAdmin):
    form = CourseAdminForm
    inlines = [TopicInline, ]
    extra = 0
    list_display = ('name', 'id', 'category', 'category_id', 'price')
    list_display_links = ('id', 'name')
    search_fields = ('name', )


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'course')
    list_display_links = ('id', 'name')
    search_fields = ('name',)


@admin.register(UploadFile)
class UploadFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'file')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'topic', 'name', 'course')
    list_display_links = ('id', 'name')
    search_fields = ('name', )
    list_filter = ('topic__course__name',)


@admin.register(UserCourse)
class UserLessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'status')
    list_display_links = ('id', 'user')
    search_fields = ('course', 'user')
    list_filter = ('course__name',)


@admin.register(UserLesson)
class UserLessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'lesson', 'status')
    list_display_links = ('id', 'user')
    search_fields = ('lesson', 'user')
    list_filter = ('lesson__topic__course__name',)


@admin.register(CourseCertificate)
class CourseCertificateAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'certificated_course')
    list_display_links = ('id', 'user', 'course', 'certificated_course')
    search_fields = ('user', 'course', 'certificated_course')
    list_filter = ('user', 'course', 'certificated_course')


@admin.register(CertificatedCourse)
class CertificatedCourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price')
    list_display_links = ('id', 'name', 'category')
    search_fields = ('name', 'category')
    list_filter = ('category', 'sub_courses')
    readonly_fields = ('price',)
