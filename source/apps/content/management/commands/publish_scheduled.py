"""Publish everything whose scheduled moment has passed.

Run it from cron every few minutes:

    */5 * * * * python manage.py publish_scheduled

Safe to run as often as you like: a piece that is already live is not in the
queue any more, and a run that publishes nothing says so and exits 0.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from source.apps.content.models import Article, Magazine


class Command(BaseCommand):
    help = "Put scheduled articles and editions live once their time has come."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="List what would go live without changing anything.",
        )

    def handle(self, *args, **options):
        now = timezone.now()
        published = 0

        for model, label in ((Article, "article"), (Magazine, "edition")):
            for item in model.objects.due(now):
                if options["dry_run"]:
                    self.stdout.write(f"would publish {label}: {item}")
                else:
                    item.go_live(item.scheduled_for or now)
                    self.stdout.write(self.style.SUCCESS(f"published {label}: {item}"))
                published += 1

        if not published:
            self.stdout.write("nothing due")
        return None
