from django.conf import settings
from django.core.management.base import BaseCommand

from source.apps.notifications.models import Notification


class Command(BaseCommand):
    help = "Delete read notifications older than NOTIFICATION_CLEANUP_DAYS (default 30)."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=getattr(settings, "NOTIFICATION_CLEANUP_DAYS", 30))

    def handle(self, *args, **options):
        deleted = Notification.cleanup_old_notifications(days=options["days"])
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} old notifications"))
