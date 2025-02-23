from celery import shared_task
from django.conf import settings
from .models import Notification

@shared_task
def cleanup_old_notifications():
    """
    Periodic task to clean up old notifications.
    Runs daily to remove read notifications older than the configured retention period.
    """
    days = getattr(settings, 'NOTIFICATION_CLEANUP_DAYS', 30)
    return Notification.cleanup_old_notifications(days=days)

@shared_task
def send_bulk_notification(user_ids, title, message, notification_type='info', link=None):
    """
    Asynchronously send notifications to multiple users.
    
    Args:
        user_ids: List of user IDs to send notifications to
        title: Notification title
        message: Notification message
        notification_type: Type of notification (info, success, warning, error)
        link: Optional URL for the notification
    """
    from django.contrib.auth import get_user_model
    from .services import NotificationService
    
    User = get_user_model()
    users = User.objects.filter(id__in=user_ids)
    
    notifications = NotificationService.create_notification(
        recipient=users,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link
    )
    
    return len(notifications)
