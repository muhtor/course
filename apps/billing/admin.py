from django.contrib import admin
from .models import Card, Transaction, BalanceTransaction, Voucher


class CardAdmin(admin.ModelAdmin):
    list_display = ('user', 'brand', 'country', 'first6', 'last4', 'masked16', 'phone', 'is_verify', 'status')


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'card', 'order_id', 'amount', 'error')
    search_fields = ['card__masked16', 'transaction_id', 'order_id', 'amount', 'status', 'error']


class BalanceTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status')


admin.site.register(BalanceTransaction, BalanceTransactionAdmin)
admin.site.register(Card, CardAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Voucher)
