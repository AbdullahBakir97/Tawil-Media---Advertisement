from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class NotificationQuerySet(models.QuerySet):
    def unread(self):
        return self.filter(read=False)

    def for_user(self, user):
        return self.filter(recipient=user)


class Notification(models.Model):
    class Type(models.TextChoices):
        INFO = "info", "Information"
        SUCCESS = "success", "Success"
        WARNING = "warning", "Warning"
        ERROR = "error", "Error"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=Type.choices, default=Type.INFO)
    link = models.URLField(blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = NotificationQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["recipient", "read"])]

    def __str__(self):
        return f"{self.title} - {self.recipient}"

    def mark_as_read(self):
        if not self.read:
            self.read = True
            self.save(update_fields=["read", "updated_at"])

    @classmethod
    def notify(cls, recipient, title, message, notification_type=Type.INFO, link=""):
        return cls.objects.create(
            recipient=recipient, title=title, message=message, notification_type=notification_type, link=link
        )

    @classmethod
    def cleanup_old_notifications(cls, days=30):
        cutoff = timezone.now() - timedelta(days=days)
        deleted, _ = cls.objects.filter(created_at__lt=cutoff, read=True).delete()
        return deleted
