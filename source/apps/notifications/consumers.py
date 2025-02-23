import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .services import NotificationService

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection."""
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        self.user = self.scope["user"]
        self.room_group_name = f"notifications_{self.user.id}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Send initial unread count
        unread_count = await self.get_unread_count()
        await self.send(json.dumps({
            'type': 'unread_count',
            'count': unread_count
        }))

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'mark_all_read':
                await self.mark_all_as_read()
                await self.send_unread_count()
            elif action == 'mark_read':
                notification_id = data.get('notification_id')
                if notification_id:
                    await self.mark_as_read(notification_id)
                    await self.send_unread_count()

        except json.JSONDecodeError:
            pass

    async def notification_message(self, event):
        """Handle notification messages from other parts of the application."""
        message = event['message']
        await self.send(text_data=json.dumps(message))

    @database_sync_to_async
    def get_unread_count(self):
        """Get unread notifications count."""
        return NotificationService.get_unread_count(self.user)

    @database_sync_to_async
    def mark_all_as_read(self):
        """Mark all notifications as read."""
        return NotificationService.mark_all_as_read(self.user)

    @database_sync_to_async
    def mark_as_read(self, notification_id):
        """Mark a specific notification as read."""
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=self.user
            )
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False

    async def send_unread_count(self):
        """Send updated unread count to the client."""
        unread_count = await self.get_unread_count()
        await self.send(json.dumps({
            'type': 'unread_count',
            'count': unread_count
        }))
