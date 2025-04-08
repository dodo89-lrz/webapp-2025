from django.contrib import admin
from .models import Account, Transaction, PaymentRequest

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'currency', 'balance']
    search_fields = ['user__username']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'amount', 'timestamp']
    search_fields = ['sender__username', 'recipient__username']

@admin.register(PaymentRequest)
class PaymentRequestAdmin(admin.ModelAdmin):
    list_display = ['requester', 'requestee', 'amount', 'is_accepted', 'is_rejected']
    search_fields = ['requester__username', 'requestee__username']
