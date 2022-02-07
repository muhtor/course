from django.contrib import admin
from .models import Cart, CartCourse


class CartCourseAdmin(admin.ModelAdmin):
    list_display = ('course', 'id', 'course_id', 'course_price', 'insert_type', 'paid', 'cart')

    # def has_change_permission(self, request, obj=None):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False
    #
    # def has_view_permission(self, request, obj=None):
    #     return True
    #
    # def has_add_permission(self, request):
    #     return False


class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'paid_courses', 'unpaid_courses', 'desire_courses', 'total', 'is_active')

    # def has_change_permission(self, request, obj=None):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False
    #
    # def has_view_permission(self, request, obj=None):
    #     return True
    #
    # def has_add_permission(self, request):
    #     return False


admin.site.register(Cart, CartAdmin)
admin.site.register(CartCourse, CartCourseAdmin)
