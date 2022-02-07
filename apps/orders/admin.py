from django.contrib import admin
from .models import OrderCheckout, CheckoutItem, Order


class OrderCheckoutAdmin(admin.ModelAdmin):
    list_display = ('user', 'id', 'all_items', 'total', 'paid', 'is_active')

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


class CheckoutItemAdmin(admin.ModelAdmin):
    list_display = ('course', 'id', 'course_id', 'checkout')

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


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'order_id', 'checkout_id', 'subtotal', 'total', 'payment_status', 'state', 'is_active')

    # def has_change_permission(self, request, obj=None):
    #     # return False
    #     return True
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False
    #
    # def has_view_permission(self, request, obj=None):
    #     return True
    #
    # def has_add_permission(self, request):
    #     return False

admin.site.register(OrderCheckout, OrderCheckoutAdmin)
admin.site.register(CheckoutItem, CheckoutItemAdmin)
admin.site.register(Order, OrderAdmin)
