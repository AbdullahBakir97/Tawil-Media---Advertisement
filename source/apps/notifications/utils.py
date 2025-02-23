from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

def send_notification_to_user(user_id, notification_data):
    """
    Send a real-time notification to a specific user.
    
    Args:
        user_id: The ID of the user to send the notification to
        notification_data: Dictionary containing notification details
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notifications_{user_id}",
        {
            "type": "notification_message",
            "message": {
                "type": "notification",
                "notification": notification_data
            }
        }
    )

def broadcast_notification(user_ids, notification_data):
    """
    Broadcast a notification to multiple users.
    
    Args:
        user_ids: List of user IDs to send the notification to
        notification_data: Dictionary containing notification details
    """
    channel_layer = get_channel_layer()
    for user_id in user_ids:
        async_to_sync(channel_layer.group_send)(
            f"notifications_{user_id}",
            {
                "type": "notification_message",
                "message": {
                    "type": "notification",
                    "notification": notification_data
                }
            }
        )

def update_notification_count(user_id, count):
    """
    Update the unread notification count for a user.
    
    Args:
        user_id: The ID of the user to update
        count: The new unread count
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notifications_{user_id}",
        {
            "type": "notification_message",
            "message": {
                "type": "unread_count",
                "count": count
            }
        }
    )
