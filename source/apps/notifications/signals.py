from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from .utils import send_notification_to_user, update_notification_count

@receiver(post_save, sender=Notification)
def notification_created(sender, instance, created, **kwargs):
    """
    Signal handler for when a new notification is created.
    Sends real-time updates via WebSocket.
    """
    if created:
        # Send the new notification to the user via WebSocket
        notification_data = {
            'id': instance.id,
            'title': instance.title,
            'message': instance.message,
            'type': instance.notification_type,
            'link': instance.link,
            'created_at': instance.created_at.isoformat(),
            'is_read': instance.is_read
        }
        send_notification_to_user(instance.recipient.id, notification_data)
        
        # Update the unread count for the user
        unread_count = Notification.objects.filter(
            recipient=instance.recipient,
            is_read=False
        ).count()
        update_notification_count(instance.recipient.id, unread_count)
