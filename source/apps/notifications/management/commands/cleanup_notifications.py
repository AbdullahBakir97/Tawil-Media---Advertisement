from django.core.management.base import BaseCommand
from django.conf import settings
from source.apps.notifications.models import Notification

class Command(BaseCommand):
    help = 'Clean up old notifications from the database'

    def handle(self, *args, **options):
        days = getattr(settings, 'NOTIFICATION_CLEANUP_DAYS', 30)
        deleted_count = Notification.cleanup_old_notifications(days=days)
        self.stdout.write(
            self.style.SUCCESS(f'Successfully cleaned up {deleted_count} old notifications')
        )
