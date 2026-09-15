from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from django.utils.translation import activate

from source.apps.events.models import Event


def an_event(when=None, **kwargs):
    kwargs.setdefault("title", "Ausgabe 12 – Release")
    kwargs.setdefault("starts_at", when or timezone.now() + timedelta(days=7))
    return Event.objects.create(**kwargs)


class EventModelTests(TestCase):
    def test_a_new_event_is_a_draft_and_not_public(self):
        event = an_event()
        self.assertEqual(event.status, "draft")
        self.assertFalse(event.is_published)
        self.assertEqual(event.slug, "ausgabe-12-release")

    def test_the_title_and_summary_read_in_the_visitors_language(self):
        event = an_event(title_de="Releaseabend", title_ar="ليلة الإصدار", summary_de="Mit Musik.")
        activate("de")
        self.assertEqual(event.label, "Releaseabend")
        self.assertEqual(event.summary, "Mit Musik.")
        activate("ar")
        self.assertEqual(event.label, "ليلة الإصدار")
        activate("de")

    def test_the_desk_title_is_used_until_a_translation_exists(self):
        self.assertEqual(an_event().label, "Ausgabe 12 – Release")

    def test_an_event_is_running_between_its_start_and_its_end(self):
        now = timezone.now()
        running = an_event(when=now - timedelta(hours=1), ends_at=now + timedelta(hours=1))
        self.assertTrue(running.is_running)
        self.assertFalse(running.has_passed)

    def test_an_event_without_an_end_runs_for_a_while_then_passes(self):
        """A launch that gives no end time is still on an hour after the doors
        open, and over by the next morning."""
        just_started = an_event(when=timezone.now() - timedelta(minutes=1))
        self.assertTrue(just_started.is_running)
        self.assertFalse(just_started.has_passed)

        last_night = an_event(slug="gestern", when=timezone.now() - timedelta(hours=12))
        self.assertFalse(last_night.is_running)
        self.assertTrue(last_night.has_passed)

    def test_the_place_reads_with_whatever_is_filled_in(self):
        self.assertEqual(an_event(venue="Aquarium", city="Berlin").place, "Aquarium · Berlin")
        self.assertEqual(an_event(slug="nur-stadt", city="Köln").place, "Köln")
        self.assertEqual(an_event(slug="leer").place, "")

    def test_an_event_over_two_days_is_marked_as_spanning(self):
        start = timezone.now() + timedelta(days=3)
        self.assertTrue(an_event(when=start, ends_at=start + timedelta(days=1)).spans_days)
        self.assertFalse(an_event(slug="ein-tag", when=start, ends_at=start + timedelta(hours=2)).spans_days)


class EventQueryTests(TestCase):
    def setUp(self):
        now = timezone.now()
        self.soon = an_event(title="Bald", slug="bald", when=now + timedelta(days=2)).go_live()
        self.later = an_event(title="Später", slug="spaeter", when=now + timedelta(days=20)).go_live()
        self.gone = an_event(title="Vorbei", slug="vorbei", when=now - timedelta(days=5)).go_live()
        self.draft = an_event(title="Entwurf", slug="entwurf", when=now + timedelta(days=1))

    def test_upcoming_is_published_only_and_soonest_first(self):
        self.assertEqual(list(Event.objects.upcoming()), [self.soon, self.later])

    def test_past_is_newest_first(self):
        self.assertEqual(list(Event.objects.past()), [self.gone])

    def test_an_event_still_running_counts_as_upcoming(self):
        now = timezone.now()
        running = an_event(title="Läuft", slug="laeuft", when=now - timedelta(hours=1), ends_at=now + timedelta(hours=2))
        running.go_live()
        self.assertIn(running, Event.objects.upcoming())
        self.assertNotIn(running, Event.objects.past())


class EventPageTests(TestCase):
    def setUp(self):
        now = timezone.now()
        self.next_event = an_event(title="Releaseabend", slug="release", when=now + timedelta(days=3),
                                   venue="Aquarium", city="Berlin", summary_de="Ein Abend mit Musik.")
        self.next_event.go_live()
        self.past_event = an_event(title="Lesung", slug="lesung", when=now - timedelta(days=10))
        self.past_event.go_live()

    def test_the_diary_leads_with_the_next_event(self):
        response = self.client.get("/events/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["next_event"], self.next_event)
        self.assertContains(response, "Releaseabend")
        self.assertContains(response, "Aquarium · Berlin")

    def test_past_events_are_listed_separately(self):
        response = self.client.get("/events/")
        self.assertEqual(list(response.context["past"]), [self.past_event])

    def test_an_empty_diary_says_so(self):
        Event.objects.all().delete()
        self.assertContains(self.client.get("/events/"), "empty-state")

    def test_the_detail_page_shows_when_and_where(self):
        response = self.client.get("/events/release/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Releaseabend")
        self.assertContains(response, "Aquarium")
        self.assertContains(response, "Ein Abend mit Musik.")

    def test_a_draft_event_is_hidden_but_opens_with_its_preview_link(self):
        draft = an_event(title="Geheim", slug="geheim")
        self.assertEqual(self.client.get("/events/geheim/").status_code, 404)
        response = self.client.get(f"/events/geheim/?preview={draft.preview_token}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "preview-banner")

    def test_staff_see_a_draft_event(self):
        an_event(title="Geheim", slug="geheim")
        self.client.force_login(
            get_user_model().objects.create_user(email="desk@example.com", password="pw-for-tests", is_staff=True)
        )
        self.assertEqual(self.client.get("/events/geheim/").status_code, 200)


class EventWorkflowTests(TestCase):
    def test_a_scheduled_event_is_published_by_the_command(self):
        event = an_event()
        event.status = "scheduled"
        event.scheduled_for = timezone.now() - timedelta(minutes=1)
        event.save()
        call_command("publish_scheduled", verbosity=0)
        event.refresh_from_db()
        self.assertTrue(event.is_published)

    def test_the_desk_lists_events_and_moves_them(self):
        event = an_event()
        self.client.force_login(
            get_user_model().objects.create_user(email="desk@example.com", password="pw-for-tests", is_staff=True)
        )
        response = self.client.get("/studio/desk/")
        self.assertContains(response, "Ausgabe 12")
        self.client.post("/studio/desk/", {"pk": event.pk, "kind": "event", "move": "live"})
        event.refresh_from_db()
        self.assertTrue(event.is_published)
