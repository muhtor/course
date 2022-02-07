from django.contrib import admin
from .models import Review


@admin.register(Review)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'rates', 'date_created')
    list_filter = ('date_created', )
