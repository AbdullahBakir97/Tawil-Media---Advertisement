from django.contrib import admin
from .models import SubscriptionPlan, Subscription, Billing, FeatureAccess, DiscountCode

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'billing_cycle', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)
    ordering = ('price',)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'start_date', 'end_date', 'is_active', 'auto_renew')
    search_fields = ('user__email', 'plan__name')
    list_filter = ('is_active', 'plan')
    ordering = ('-start_date',)

@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'amount', 'payment_date', 'payment_method', 'status')
    search_fields = ('subscription__user__email', 'subscription__plan__name')
    list_filter = ('status', 'payment_method')
    ordering = ('-payment_date',)

@admin.register(FeatureAccess)
class FeatureAccessAdmin(admin.ModelAdmin):
    list_display = ('plan', 'feature_name', 'is_available')
    search_fields = ('feature_name',)
    list_filter = ('plan', 'is_available')
    ordering = ('plan', 'feature_name')

@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'plan', 'discount_percentage', 'start_date', 'end_date', 'is_active')
    search_fields = ('code', 'plan__name')
    list_filter = ('is_active',)
    ordering = ('-start_date',)
