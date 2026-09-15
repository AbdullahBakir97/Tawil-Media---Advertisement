from django.core.management.base import BaseCommand, CommandError

from source.apps.content.models import Magazine
from source.apps.studio.services import render_magazine_pages


class Command(BaseCommand):
    help = "Render the PDF of one or all editions into flip-book pages."

    def add_arguments(self, parser):
        parser.add_argument("slug", nargs="?", help="Magazine slug; omit for every edition with a PDF.")

    def handle(self, *args, **options):
        qs = Magazine.objects.exclude(pdf="")
        if options["slug"]:
            qs = qs.filter(slug=options["slug"])
            if not qs.exists():
                raise CommandError(f"No edition with a PDF and slug {options['slug']!r}.")
        for magazine in qs:
            count = render_magazine_pages(magazine)
            self.stdout.write(f"{magazine.slug}: {count} pages")
