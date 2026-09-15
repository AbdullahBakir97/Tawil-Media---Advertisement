"""Send the newsletter issues whose moment has come.

Run it from cron beside publish_scheduled:

    */5 * * * * python manage.py send_newsletter

An issue that has already gone out is never sent again, so running this twice
costs nothing.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from source.apps.newsletter.models import Issue
from source.apps.newsletter.sending import send_issue


class Command(BaseCommand):
    help = "Send scheduled newsletter issues that are due."

    def add_arguments(self, parser):
        parser.add_argument("--issue", type=int, help="Send this issue now, whatever its schedule says.")
        parser.add_argument("--dry-run", action="store_true", help="Say what would go out, send nothing.")

    def handle(self, *args, **options):
        if options["issue"]:
            due = Issue.objects.filter(pk=options["issue"]).exclude(status=Issue.SENT)
        else:
            due = Issue.objects.filter(status=Issue.SCHEDULED, scheduled_for__lte=timezone.now())

        if not due:
            self.stdout.write("nothing due")
            return

        for issue in due:
            if options["dry_run"]:
                self.stdout.write(f"would send “{issue.subject}” to {issue.recipients().count()} subscribers")
                continue
            sent = send_issue(issue)
            self.stdout.write(self.style.SUCCESS(f"sent “{issue.subject}” to {sent} subscribers"))
