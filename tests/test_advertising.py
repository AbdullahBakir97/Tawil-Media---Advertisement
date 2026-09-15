import json
from decimal import Decimal

from django.core import mail
from django.test import TestCase

from source.apps.advertisements.models import CampaignRequest, MediaKit, RateCard
from source.apps.content.models import Magazine


class AdvertisingHubTests(TestCase):
    def setUp(self):
        self.page = RateCard.objects.create(
            slug="print-full-page", channel="print", name_de="1/1 Seite", price=Decimal("1200"), unit="edition"
        )
        RateCard.objects.create(
            slug="digital-rectangle", channel="digital", name_de="Rectangle", price=Decimal("350"), unit="week"
        )
        RateCard.objects.create(slug="retired", channel="print", name_de="Alt", price=Decimal("99"), is_active=False)

    def test_hub_lists_active_rates_only(self):
        response = self.client.get("/advertise/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1/1 Seite")
        self.assertContains(response, "Rectangle")
        self.assertNotContains(response, "Alt")

    def test_hub_offers_the_media_kit_when_there_is_one(self):
        self.assertNotContains(self.client.get("/advertise/"), "media-kit")
        MediaKit.objects.create(title="Mediadaten", file="advertising/media-kit/2026.pdf", year=2026)
        self.assertContains(self.client.get("/advertise/"), "advertising/media-kit/2026.pdf")

    def test_size_preview_uses_the_entered_dimensions(self):
        self.page.width, self.page.height = 210, 297
        self.page.save()
        self.assertEqual(self.page.aspect_ratio, "210 / 297")
        self.assertEqual(self.page.size_label, "210 × 297 mm")
        self.assertContains(self.client.get("/advertise/"), "aspect-ratio: 210 / 297")


class CampaignRequestTests(TestCase):
    def setUp(self):
        self.page = RateCard.objects.create(
            slug="print-full-page", channel="print", name_de="1/1 Seite", price=Decimal("1200"), unit="edition"
        )
        self.banner = RateCard.objects.create(
            slug="digital-rectangle", channel="digital", name_de="Rectangle", price=Decimal("350"), unit="week"
        )
        self.edition = Magazine.objects.create(title="Edition One", slug="edition-one")
        self.edition.publish()

    def post(self, **overrides):
        data = {
            "company": "Beispiel GmbH",
            "contact_name": "A. Muster",
            "email": "a@example.com",
            "phone": "",
            "message": "",
            "consent": "on",
            "selection": json.dumps({"print-full-page": 2, "digital-rectangle": 1}),
            "edition_ids": str(self.edition.pk),
        }
        data.update(overrides)
        return self.client.post("/advertise/request/", data)

    def test_request_is_stored_with_prices_from_the_database(self):
        response = self.post()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "planner-done")

        request_obj = CampaignRequest.objects.get()
        self.assertEqual(request_obj.estimate, Decimal("2750"))
        self.assertEqual(request_obj.total, Decimal("2750"))
        self.assertEqual(request_obj.items.count(), 2)
        self.assertEqual(list(request_obj.editions.all()), [self.edition])

    def test_a_tampered_price_cannot_change_the_estimate(self):
        self.post(selection=json.dumps({"print-full-page": 1}), estimate="1")
        self.assertEqual(CampaignRequest.objects.get().estimate, Decimal("1200"))

    def test_unknown_and_inactive_placements_are_dropped(self):
        RateCard.objects.create(slug="retired", channel="print", name_de="Alt", price=Decimal("99"), is_active=False)
        self.post(selection=json.dumps({"print-full-page": 1, "retired": 5, "does-not-exist": 3}))
        request_obj = CampaignRequest.objects.get()
        self.assertEqual(request_obj.items.count(), 1)
        self.assertEqual(request_obj.estimate, Decimal("1200"))

    def test_an_empty_selection_is_rejected(self):
        response = self.post(selection="{}")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(CampaignRequest.objects.exists())

    def test_consent_is_required(self):
        response = self.post(consent="")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(CampaignRequest.objects.exists())

    def test_quantities_are_capped(self):
        self.post(selection=json.dumps({"print-full-page": 5000}))
        self.assertEqual(CampaignRequest.objects.get().items.get().quantity, 99)

    def test_the_desk_is_notified(self):
        self.post()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Beispiel GmbH", mail.outbox[0].subject)
        self.assertIn("2750", mail.outbox[0].body)

    def test_get_is_not_allowed(self):
        self.assertEqual(self.client.get("/advertise/request/").status_code, 405)
