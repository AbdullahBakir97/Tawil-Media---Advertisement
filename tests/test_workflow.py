from datetime import timedelta
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from source.apps.content.models import Article, Magazine


def an_article(**kwargs):
    kwargs.setdefault("title", "Die Stadt am Morgen")
    kwargs.setdefault("content", "Ein Text über Berlin. " * 20)
    return Article.objects.create(**kwargs)


class StatusTests(TestCase):
    def test_a_new_article_starts_as_a_draft_and_is_not_live(self):
        article = an_article()
        self.assertEqual(article.status, "draft")
        self.assertFalse(article.is_published)
        self.assertIsNone(article.published_at)
        self.assertNotIn(article, Article.objects.published())

    def test_publishing_stamps_the_date_and_shows_the_article(self):
        article = an_article().go_live()
        self.assertEqual(article.status, "published")
        self.assertTrue(article.is_published)
        self.assertIsNotNone(article.published_at)
        self.assertIn(article, Article.objects.published())

    def test_taking_a_piece_down_clears_the_date_and_stays_down(self):
        article = an_article().go_live()
        article.unpublish()
        article.refresh_from_db()
        self.assertEqual(article.status, "draft")
        self.assertFalse(article.is_published)
        self.assertIsNone(article.published_at)

    def test_creating_with_is_published_still_publishes(self):
        """Older code and fixtures set the flag directly; that keeps working."""
        article = an_article(is_published=True)
        self.assertEqual(article.status, "published")
        self.assertTrue(article.is_published)

    def test_a_note_travels_with_the_piece(self):
        article = an_article().send_to_review("Foto fehlt noch")
        self.assertEqual(article.status, "review")
        self.assertEqual(article.editor_note, "Foto fehlt noch")
        self.assertFalse(article.is_published)


class ScheduleTests(TestCase):
    def test_scheduling_queues_the_article_without_publishing_it(self):
        when = timezone.now() + timedelta(days=1)
        article = an_article().schedule(when)
        self.assertEqual(article.status, "scheduled")
        self.assertEqual(article.scheduled_for, when)
        self.assertFalse(article.is_published)
        self.assertNotIn(article, Article.objects.published())

    def test_a_time_already_past_publishes_at_once(self):
        article = an_article().schedule(timezone.now() - timedelta(minutes=5))
        self.assertEqual(article.status, "published")
        self.assertTrue(article.is_published)

    def test_only_pieces_whose_time_has_come_are_due(self):
        soon = an_article(title="Bald").schedule(timezone.now() + timedelta(hours=1))
        overdue = an_article(title="Überfällig", slug="ueberfaellig")
        overdue.status, overdue.scheduled_for = "scheduled", timezone.now() - timedelta(minutes=1)
        overdue.save()
        due = list(Article.objects.due())
        self.assertIn(overdue, due)
        self.assertNotIn(soon, due)
        self.assertTrue(overdue.is_due)
        self.assertFalse(soon.is_due)


class PublishScheduledCommandTests(TestCase):
    def setUp(self):
        self.article = an_article()
        self.article.status = "scheduled"
        self.article.scheduled_for = timezone.now() - timedelta(minutes=2)
        self.article.save()

        self.edition = Magazine.objects.create(title="Ausgabe 12", slug="ausgabe-12")
        self.edition.status = "scheduled"
        self.edition.scheduled_for = timezone.now() - timedelta(minutes=2)
        self.edition.save()

    def run_command(self, *args):
        out = StringIO()
        call_command("publish_scheduled", *args, stdout=out)
        return out.getvalue()

    def test_due_pieces_go_live(self):
        output = self.run_command()
        self.article.refresh_from_db()
        self.edition.refresh_from_db()
        self.assertTrue(self.article.is_published)
        self.assertTrue(self.edition.is_published)
        self.assertIn("published article", output)
        self.assertIn("published edition", output)

    def test_the_published_date_is_the_scheduled_moment_not_the_run_time(self):
        self.run_command()
        self.article.refresh_from_db()
        self.assertEqual(self.article.published_at, self.article.scheduled_for)

    def test_a_dry_run_changes_nothing(self):
        output = self.run_command("--dry-run")
        self.article.refresh_from_db()
        self.assertFalse(self.article.is_published)
        self.assertIn("would publish", output)

    def test_running_twice_publishes_nothing_the_second_time(self):
        self.run_command()
        self.assertIn("nothing due", self.run_command())


class PreviewTests(TestCase):
    def setUp(self):
        self.article = an_article(slug="vorschau")

    def test_a_draft_is_hidden_from_the_public(self):
        self.assertEqual(self.client.get("/articles/vorschau/").status_code, 404)

    def test_the_preview_link_opens_the_draft_and_says_so(self):
        response = self.client.get(f"/articles/vorschau/?preview={self.article.preview_token}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "preview-banner")

    def test_a_wrong_token_is_still_a_404(self):
        self.assertEqual(
            self.client.get("/articles/vorschau/?preview=00000000-0000-0000-0000-000000000000").status_code, 404
        )

    def test_staff_see_the_draft_without_a_token(self):
        self.client.force_login(
            get_user_model().objects.create_user(email="desk@example.com", password="pw-for-tests", is_staff=True)
        )
        self.assertEqual(self.client.get("/articles/vorschau/").status_code, 200)

    def test_a_published_article_shows_no_preview_banner(self):
        self.article.go_live()
        response = self.client.get("/articles/vorschau/")
        self.assertNotContains(response, "preview-banner")

    def test_an_edition_preview_works_the_same_way(self):
        edition = Magazine.objects.create(title="Ausgabe 13", slug="ausgabe-13")
        self.assertEqual(self.client.get("/magazines/ausgabe-13/").status_code, 404)
        self.assertEqual(
            self.client.get(f"/magazines/ausgabe-13/?preview={edition.preview_token}").status_code, 200
        )


class DeskTests(TestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user(
            email="desk@example.com", password="pw-for-tests", is_staff=True
        )
        self.article = an_article(slug="desk-stueck")

    def test_the_desk_is_staff_only(self):
        self.assertEqual(self.client.get("/studio/desk/").status_code, 302)
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get("/studio/desk/").status_code, 200)

    def test_a_piece_can_be_moved_along(self):
        self.client.force_login(self.staff)
        self.client.post("/studio/desk/", {"pk": self.article.pk, "kind": "article", "move": "review"})
        self.article.refresh_from_db()
        self.assertEqual(self.article.status, "review")

        self.client.post("/studio/desk/", {"pk": self.article.pk, "kind": "article", "move": "live"})
        self.article.refresh_from_db()
        self.assertTrue(self.article.is_published)

    def test_a_piece_can_be_scheduled_from_the_desk(self):
        self.client.force_login(self.staff)
        when = (timezone.now() + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M")
        self.client.post(
            "/studio/desk/", {"pk": self.article.pk, "kind": "article", "move": "schedule", "when": when}
        )
        self.article.refresh_from_db()
        self.assertEqual(self.article.status, "scheduled")
        self.assertIsNotNone(self.article.scheduled_for)

    def test_an_unreadable_date_changes_nothing(self):
        self.client.force_login(self.staff)
        self.client.post(
            "/studio/desk/", {"pk": self.article.pk, "kind": "article", "move": "schedule", "when": "morgen"}
        )
        self.article.refresh_from_db()
        self.assertEqual(self.article.status, "draft")

    def test_the_board_shows_each_piece_in_its_column(self):
        an_article(title="In Prüfung", slug="in-pruefung").send_to_review()
        self.client.force_login(self.staff)
        response = self.client.get("/studio/desk/")
        self.assertContains(response, "desk-column--draft")
        self.assertContains(response, "desk-column--review")
        self.assertContains(response, "In Prüfung")
