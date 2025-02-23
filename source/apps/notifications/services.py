from typing import Optional, Union, List
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from .models import Notification

User = get_user_model()

class NotificationService:
    @staticmethod
    def create_notification(
        recipient: Union[User, QuerySet, List[User]],
        title: str,
        message: str,
        notification_type: str = 'info',
        link: Optional[str] = None
    ) -> Union[Notification, List[Notification]]:
        """
        Create a notification for one or multiple recipients.
        
        Args:
            recipient: User object, QuerySet of users, or list of users
            title: Notification title
            message: Notification message
            notification_type: Type of notification (info, success, warning, error)
            link: Optional URL for the notification
            
        Returns:
            Single notification or list of notifications
        """
        if isinstance(recipient, (QuerySet, list)):
            notifications = []
            for user in recipient:
                notifications.append(
                    Notification.create(
                        recipient=user,
                        title=title,
                        message=message,
                        notification_type=notification_type,
                        link=link
                    )
                )
            return notifications
        
        return Notification.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link
        )

    @staticmethod
    def mark_all_as_read(user: User) -> int:
        """Mark all unread notifications as read for a user."""
        notifications = Notification.objects.filter(recipient=user, read=False)
        count = notifications.count()
        notifications.update(read=True)
        
        # Update Redis cache
        redis_key = f"user:{user.id}:notifications"
        notifications = Notification.get_recent_notifications(user)
        for notification in notifications:
            notification['read'] = True
        
        return count

    @staticmethod
    def get_unread_count(user: User) -> int:
        """Get the number of unread notifications for a user."""
        notifications = Notification.get_recent_notifications(user)
        return sum(1 for n in notifications if not n['read'])

    @staticmethod
    def delete_notification(user: User, notification_id: int) -> bool:
        """Delete a specific notification."""
        try:
            notification = Notification.objects.get(id=notification_id, recipient=user)
            notification.delete()
            return True
        except Notification.DoesNotExist:
            return False
