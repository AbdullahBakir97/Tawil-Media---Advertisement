"""Project-level guards: migrations in sync, admin loads."""

from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse


class ProjectHealthTests(TestCase):
    def test_no_missing_migrations(self):
        out = StringIO()
        call_command("makemigrations", "--check", "--dry-run", stdout=out)

    def test_admin_index_and_changelists_load(self):
        admin = get_user_model().objects.create_superuser(email="root@example.com", password="a-long-passw0rd!")
        self.client.force_login(admin)
        self.assertEqual(self.client.get(reverse("admin:index")).status_code, 200)
        for url_name in ("admin:users_user_changelist", "admin:content_article_changelist", "admin:archives_edition_changelist"):
            with self.subTest(url=url_name):
                self.assertEqual(self.client.get(reverse(url_name)).status_code, 200)
