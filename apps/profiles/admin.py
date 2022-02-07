from django.contrib import admin

from .models import Profile, Notification, NotificationCategory


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'country', 'city')


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('get_user_phone', 'title', 'show_status', 'id')
    list_filter = ('profile', 'show_status')
    list_display_links = ('get_user_phone', 'title')
    search_fields = ('title',)

    def get_user_phone(self, obj):
        return obj.profile.user.phone

    get_user_phone.short_description = 'User'
    get_user_phone.admin_order_field = 'profile__user__phone'


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(NotificationCategory)
