from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "recipient", "notification_type", "read", "created_at")
    list_filter = ("notification_type", "read")
    search_fields = ("title", "message", "recipient__email")
    date_hierarchy = "created_at"
    raw_id_fields = ("recipient",)
