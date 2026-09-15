from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from source.apps.content.models import Article, Magazine
from source.apps.events.models import Event
from source.apps.newsletter.composer import plain_text, render_issue, site_url
from source.apps.newsletter.models import Issue, IssueBlock, NewsletterSubscriber
from source.apps.newsletter.sending import send_issue
from source.apps.studio.models import AdSlot


def an_article(**kwargs):
    kwargs.setdefault("title", "Die Stadt am Morgen")
    kwargs.setdefault("content", "Ein Text über Berlin. " * 20)
    return Article.objects.create(**kwargs).go_live()


class SubscriberTests(TestCase):
    def test_signing_up_records_the_language_of_the_page(self):
        self.client.post("/newsletter/subscribe/", {"email": "a@example.com"})
        self.assertEqual(NewsletterSubscriber.objects.get(email="a@example.com").language, "de")

        self.client.post("/en/newsletter/subscribe/", {"email": "b@example.com"})
        self.assertEqual(NewsletterSubscriber.objects.get(email="b@example.com").language, "en")

    def test_every_subscriber_gets_an_unguessable_token(self):
        first = NewsletterSubscriber.objects.create(email="a@example.com")
        second = NewsletterSubscriber.objects.create(email="b@example.com")
        self.assertNotEqual(first.token, second.token)
        self.assertIn(str(first.token), first.unsubscribe_url())


class UnsubscribeTests(TestCase):
    def setUp(self):
        self.subscriber = NewsletterSubscriber.objects.create(email="a@example.com")

    def test_opening_the_link_only_asks(self):
        """A mail client that prefetches the link must not unsubscribe anybody."""
        response = self.client.get(self.subscriber.unsubscribe_url())
        self.assertEqual(response.status_code, 200)
        self.subscriber.refresh_from_db()
        self.assertTrue(self.subscriber.is_active)

    def test_confirming_takes_them_off_the_list(self):
        response = self.client.post(self.subscriber.unsubscribe_url())
        self.assertEqual(response.status_code, 200)
        self.subscriber.refresh_from_db()
        self.assertFalse(self.subscriber.is_active)

    def test_an_unknown_token_is_a_404(self):
        self.assertEqual(
            self.client.get("/newsletter/unsubscribe/00000000-0000-0000-0000-000000000000/").status_code, 404
        )


class BlockTests(TestCase):
    def setUp(self):
        self.issue = Issue.objects.create(subject="Diese Woche")

    def test_a_block_borrows_the_title_of_what_it_points_at(self):
        block = IssueBlock.objects.create(issue=self.issue, kind="article", article=an_article())
        self.assertEqual(block.title, "Die Stadt am Morgen")
        self.assertFalse(block.is_empty)

    def test_a_heading_overrides_the_borrowed_title(self):
        block = IssueBlock.objects.create(issue=self.issue, kind="article", article=an_article(), heading="Unser Tipp")
        self.assertEqual(block.title, "Unser Tipp")

    def test_a_block_pointing_at_nothing_is_empty(self):
        self.assertTrue(IssueBlock.objects.create(issue=self.issue, kind="article").is_empty)
        self.assertTrue(IssueBlock.objects.create(issue=self.issue, kind="text").is_empty)
        self.assertFalse(IssueBlock.objects.create(issue=self.issue, kind="text", body="Hallo").is_empty)


class RenderTests(TestCase):
    def setUp(self):
        self.issue = Issue.objects.create(subject="Diese Woche", preheader="Drei Geschichten", intro="Guten Morgen.")
        self.article = an_article()
        IssueBlock.objects.create(issue=self.issue, kind="lead", article=self.article, order=0)

    def test_the_mail_carries_the_copy_and_an_absolute_link(self):
        html = render_issue(self.issue)
        self.assertIn("Diese Woche", html)
        self.assertIn("Guten Morgen.", html)
        self.assertIn("Die Stadt am Morgen", html)
        self.assertIn(f"{site_url()}{self.article.get_absolute_url()}", html)

    def test_relative_links_never_survive_into_the_mail(self):
        """An inbox has no origin, so every href must be absolute."""
        html = render_issue(self.issue)
        self.assertNotIn('href="/', html)

    def test_a_block_that_points_at_nothing_is_left_out(self):
        IssueBlock.objects.create(issue=self.issue, kind="event", order=1)
        self.assertEqual(render_issue(self.issue).count("<h2"), 0)

    def test_the_preview_never_carries_somebodys_token(self):
        subscriber = NewsletterSubscriber.objects.create(email="a@example.com")
        self.assertNotIn(str(subscriber.token), render_issue(self.issue))
        self.assertIn(str(subscriber.token), render_issue(self.issue, subscriber))

    def test_the_plain_text_version_lists_everything(self):
        text = plain_text(self.issue)
        self.assertIn("Diese Woche", text)
        self.assertIn("Die Stadt am Morgen", text)
        self.assertIn(site_url(), text)

    def test_an_event_block_carries_its_date(self):
        event = Event.objects.create(title="Releaseabend", starts_at=timezone.now() + timedelta(days=3), city="Berlin")
        event.go_live()
        IssueBlock.objects.create(issue=self.issue, kind="event", event=event, order=1)
        self.assertIn("Berlin", render_issue(self.issue))


class SendingTests(TestCase):
    def setUp(self):
        self.issue = Issue.objects.create(subject="Diese Woche")
        IssueBlock.objects.create(issue=self.issue, kind="lead", article=an_article())
        NewsletterSubscriber.objects.create(email="de1@example.com", language="de")
        NewsletterSubscriber.objects.create(email="de2@example.com", language="de")
        NewsletterSubscriber.objects.create(email="ar@example.com", language="ar")
        NewsletterSubscriber.objects.create(email="gone@example.com", language="de", is_active=False)

    def test_only_active_subscribers_of_that_language_receive_it(self):
        sent = send_issue(self.issue)
        self.assertEqual(sent, 2)
        recipients = sorted(address for message in mail.outbox for address in message.to)
        self.assertEqual(recipients, ["de1@example.com", "de2@example.com"])

    def test_the_issue_is_marked_sent_with_its_count(self):
        send_issue(self.issue)
        self.issue.refresh_from_db()
        self.assertEqual(self.issue.status, Issue.SENT)
        self.assertEqual(self.issue.sent_count, 2)
        self.assertIsNotNone(self.issue.sent_at)

    def test_an_issue_is_never_sent_twice(self):
        send_issue(self.issue)
        mail.outbox.clear()
        self.assertEqual(send_issue(self.issue), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_every_message_carries_an_unsubscribe_header_and_link(self):
        send_issue(self.issue)
        message = mail.outbox[0]
        self.assertIn("List-Unsubscribe", message.extra_headers)
        subscriber = NewsletterSubscriber.objects.get(email=message.to[0])
        self.assertIn(str(subscriber.token), message.alternatives[0][0])

    def test_the_command_sends_what_is_due_and_nothing_else(self):
        self.issue.status = Issue.SCHEDULED
        self.issue.scheduled_for = timezone.now() - timedelta(minutes=1)
        self.issue.save()
        later = Issue.objects.create(subject="Später", status=Issue.SCHEDULED,
                                     scheduled_for=timezone.now() + timedelta(days=1))
        call_command("send_newsletter", verbosity=0)
        self.issue.refresh_from_db()
        later.refresh_from_db()
        self.assertEqual(self.issue.status, Issue.SENT)
        self.assertEqual(later.status, Issue.SCHEDULED)

    def test_a_dry_run_sends_nothing(self):
        self.issue.status = Issue.SCHEDULED
        self.issue.scheduled_for = timezone.now() - timedelta(minutes=1)
        self.issue.save()
        call_command("send_newsletter", "--dry-run", verbosity=0)
        self.issue.refresh_from_db()
        self.assertEqual(self.issue.status, Issue.SCHEDULED)
        self.assertEqual(len(mail.outbox), 0)


@override_settings(SITE_URL="https://almadina.example")
class ComposerViewTests(TestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user(
            email="desk@example.com", password="pw-for-tests", is_staff=True
        )
        self.client.force_login(self.staff)
        self.issue = Issue.objects.create(subject="Diese Woche")
        self.article = an_article()

    def test_the_composer_is_staff_only(self):
        self.client.logout()
        self.assertEqual(self.client.get("/studio/newsletter/").status_code, 302)
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get("/studio/newsletter/").status_code, 200)

    def test_a_block_can_be_added_and_removed(self):
        url = f"/studio/newsletter/{self.issue.pk}/"
        self.client.post(url, {"action": "add-block", "kind": "lead", "target": self.article.pk})
        block = self.issue.blocks.get()
        self.assertEqual(block.article, self.article)

        self.client.post(url, {"action": "remove-block", "block": block.pk})
        self.assertEqual(self.issue.blocks.count(), 0)

    def test_blocks_can_be_reordered(self):
        first = IssueBlock.objects.create(issue=self.issue, kind="article", article=self.article, order=0)
        second = IssueBlock.objects.create(issue=self.issue, kind="text", body="Zweitens", order=1)
        self.client.post(f"/studio/newsletter/{self.issue.pk}/",
                         {"action": "move-block", "block": second.pk, "direction": "up"})
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertEqual(second.order, 0)
        self.assertEqual(first.order, 1)

    def test_an_issue_can_be_queued_and_taken_out_again(self):
        url = f"/studio/newsletter/{self.issue.pk}/"
        when = (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
        self.client.post(url, {"action": "schedule", "when": when})
        self.issue.refresh_from_db()
        self.assertEqual(self.issue.status, Issue.SCHEDULED)

        self.client.post(url, {"action": "unschedule"})
        self.issue.refresh_from_db()
        self.assertEqual(self.issue.status, Issue.DRAFT)
        self.assertIsNone(self.issue.scheduled_for)

    def test_an_unreadable_date_leaves_the_issue_alone(self):
        self.client.post(f"/studio/newsletter/{self.issue.pk}/", {"action": "schedule", "when": "morgen"})
        self.issue.refresh_from_db()
        self.assertEqual(self.issue.status, Issue.DRAFT)

    def test_a_test_send_does_not_change_the_status(self):
        IssueBlock.objects.create(issue=self.issue, kind="lead", article=self.article)
        self.client.post(f"/studio/newsletter/{self.issue.pk}/", {"action": "test", "email": "me@example.com"})
        self.issue.refresh_from_db()
        self.assertEqual(self.issue.status, Issue.DRAFT)
        self.assertEqual(mail.outbox[0].to, ["me@example.com"])
        self.assertIn("[Test]", mail.outbox[0].subject)

    def test_a_sent_issue_can_no_longer_be_edited(self):
        IssueBlock.objects.create(issue=self.issue, kind="lead", article=self.article)
        send_issue(self.issue)
        self.client.post(f"/studio/newsletter/{self.issue.pk}/",
                         {"action": "add-block", "kind": "text", "body": "Nachtrag"})
        self.assertEqual(self.issue.blocks.count(), 1)

    def test_the_preview_renders_the_real_mail(self):
        IssueBlock.objects.create(issue=self.issue, kind="lead", article=self.article)
        response = self.client.get(f"/studio/newsletter/{self.issue.pk}/preview/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Die Stadt am Morgen")
        self.assertEqual(response["X-Frame-Options"], "SAMEORIGIN")

    def test_an_edition_and_an_ad_can_be_added(self):
        edition = Magazine.objects.create(title="Ausgabe 13", slug="ausgabe-13")
        edition.publish()
        ad = AdSlot.objects.create(key="newsletter-banner", advertiser="Beispiel GmbH",
                                   image="studio/ads/x.png", url="https://example.com")
        url = f"/studio/newsletter/{self.issue.pk}/"
        self.client.post(url, {"action": "add-block", "kind": "edition", "target": edition.pk})
        self.client.post(url, {"action": "add-block", "kind": "ad", "target": ad.pk})
        self.assertEqual(self.issue.blocks.count(), 2)
        self.assertFalse(any(block.is_empty for block in self.issue.blocks.all()))
