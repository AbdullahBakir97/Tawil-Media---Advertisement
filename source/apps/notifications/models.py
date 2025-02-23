from django.db import models
from django.conf import settings
import json
from datetime import datetime, timedelta
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from redis import Redis
from django.conf import settings

redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='info'
    )
    link = models.URLField(blank=True, null=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.recipient.email}"

    @classmethod
    def create(cls, recipient, title, message, notification_type='info', link=None):
        """Create a notification and store in both Redis and database."""
        # Create notification in database
        notification = cls.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link
        )

        # Store in Redis for quick access
        notification_data = {
            'id': notification.id,
            'title': title,
            'message': message,
            'type': notification_type,
            'link': link,
            'read': False,
            'created_at': notification.created_at.isoformat(),
        }

        # Add to user's recent notifications list in Redis
        redis_key = f"user:{recipient.id}:notifications"
        redis_client.lpush(redis_key, json.dumps(notification_data, cls=DjangoJSONEncoder))
        redis_client.ltrim(redis_key, 0, 99)  # Keep only last 100 notifications in Redis
        
        # Set expiry for Redis notifications (e.g., 30 days)
        redis_client.expire(redis_key, 60 * 60 * 24 * 30)

        return notification

    @classmethod
    def get_recent_notifications(cls, user, limit=10):
        """Get recent notifications from Redis, falling back to database."""
        redis_key = f"user:{user.id}:notifications"
        
        # Try to get from Redis first
        notifications = []
        redis_notifications = redis_client.lrange(redis_key, 0, limit - 1)
        
        if redis_notifications:
            for notification_json in redis_notifications:
                try:
                    notifications.append(json.loads(notification_json))
                except json.JSONDecodeError:
                    continue
        else:
            # Fallback to database if Redis is empty
            db_notifications = cls.objects.filter(recipient=user)[:limit]
            notifications = [{
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'type': n.notification_type,
                'link': n.link,
                'read': n.read,
                'created_at': n.created_at.isoformat(),
            } for n in db_notifications]
            
            # Repopulate Redis
            for notification in reversed(notifications):
                redis_client.lpush(redis_key, json.dumps(notification, cls=DjangoJSONEncoder))
            redis_client.expire(redis_key, 60 * 60 * 24 * 30)  # 30 days expiry

        return notifications

    def mark_as_read(self):
        """Mark notification as read in both Redis and database."""
        if not self.read:
            # Update database
            self.read = True
            self.save()

            # Update Redis
            redis_key = f"user:{self.recipient.id}:notifications"
            notifications = redis_client.lrange(redis_key, 0, -1)
            
            for idx, notification_json in enumerate(notifications):
                try:
                    notification_data = json.loads(notification_json)
                    if notification_data['id'] == self.id:
                        notification_data['read'] = True
                        redis_client.lset(redis_key, idx, json.dumps(notification_data, cls=DjangoJSONEncoder))
                        break
                except (json.JSONDecodeError, KeyError):
                    continue

    @classmethod
    def cleanup_old_notifications(cls, days=30):
        """Clean up old notifications from database."""
        cutoff_date = timezone.now() - timedelta(days=days)
        cls.objects.filter(created_at__lt=cutoff_date, read=True).delete()
