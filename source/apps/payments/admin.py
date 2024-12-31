from django.contrib import admin
from .models import PaymentMethod, Payment, Refund, Invoice, TransactionLog

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'is_active')
    search_fields = ('name', 'provider')
    list_filter = ('is_active',)
    ordering = ('name',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'currency', 'status', 'payment_date')
    search_fields = ('transaction_id', 'user__email')
    list_filter = ('status', 'method', 'subscription')
    ordering = ('-payment_date',)

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('payment', 'amount', 'status', 'initiated_at', 'completed_at')
    search_fields = ('payment__transaction_id',)
    list_filter = ('status',)
    ordering = ('-initiated_at',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'payment', 'issued_date', 'due_date', 'amount', 'currency')
    search_fields = ('invoice_number', 'payment__transaction_id')
    list_filter = ('currency',)
    ordering = ('-issued_date',)

@admin.register(TransactionLog)
class TransactionLogAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'type', 'created_at')
    search_fields = ('transaction_id',)
    list_filter = ('type',)
    ordering = ('-created_at',)
