from decimal import Decimal
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from source.apps.advertisements.models import CampaignRequest, CampaignRequestItem, MediaKit, RateCard


def a_file(name="kit.pdf"):
    return SimpleUploadedFile(name, b"%PDF-1.4 fake", content_type="application/pdf")


def an_image(name="x.png"):
    buffer = BytesIO()
    Image.new("RGB", (40, 30), (11, 37, 69)).save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


def a_rate(name="Ganze Seite", price="900.00", **extra):
    return RateCard.objects.create(name_de=name, slug=name.lower().replace(" ", "-"),
                                   price=Decimal(price), **extra)


def an_enquiry(company="Beispiel GmbH", status="new", rate=None, quantity=1):
    enquiry = CampaignRequest.objects.create(
        company=company, contact_name="A. Muster", email="a@example.com", status=status,
    )
    if rate:
        CampaignRequestItem.objects.create(request=enquiry, rate_card=rate,
                                           quantity=quantity, unit_price=rate.price)
    return enquiry


class Staff(TestCase):
    def setUp(self):
        self.client.force_login(
            get_user_model().objects.create_user(email="desk@example.com", password="pw-for-tests", is_staff=True)
        )


class EnquiryInboxTests(Staff):
    def test_the_inbox_is_staff_only(self):
        self.client.logout()
        self.assertEqual(self.client.get("/studio/advertising/").status_code, 302)

    def test_an_enquiry_is_listed_with_its_contact_and_its_lines(self):
        an_enquiry(rate=a_rate(), quantity=2)
        response = self.client.get("/studio/advertising/")
        self.assertContains(response, "Beispiel GmbH")
        self.assertContains(response, "a@example.com")
        self.assertContains(response, "Ganze Seite")
        self.assertContains(response, "1800")          # 2 × 900

    def test_open_enquiries_are_shown_by_default(self):
        an_enquiry(company="Nordwind GmbH", status="new")
        an_enquiry(company="Südlicht AG", status="lost")
        response = self.client.get("/studio/advertising/")
        self.assertContains(response, "Nordwind GmbH")
        self.assertNotContains(response, "Südlicht AG")

    def test_a_single_status_can_be_listed(self):
        an_enquiry(company="Ostwerk", status="won")
        an_enquiry(company="Westrand", status="new")
        response = self.client.get("/studio/advertising/?status=won")
        self.assertContains(response, "Ostwerk")
        self.assertNotContains(response, "Westrand")

    def test_everything_can_be_listed(self):
        an_enquiry(company="Südlicht AG", status="lost")
        self.assertContains(self.client.get("/studio/advertising/?status=all"), "Südlicht AG")

    def test_a_nonsense_status_falls_back_to_the_open_ones(self):
        an_enquiry(company="Nordwind GmbH", status="new")
        an_enquiry(company="Südlicht AG", status="lost")
        response = self.client.get("/studio/advertising/?status=unsinn")
        self.assertContains(response, "Nordwind GmbH")
        self.assertNotContains(response, "Südlicht AG")

    def test_the_status_can_be_moved_along(self):
        enquiry = an_enquiry()
        self.client.post("/studio/advertising/", {"pk": enquiry.pk, "status": "quoted", "back": "open"})
        enquiry.refresh_from_db()
        self.assertEqual(enquiry.status, "quoted")

    def test_an_unknown_status_changes_nothing(self):
        enquiry = an_enquiry()
        self.client.post("/studio/advertising/", {"pk": enquiry.pk, "status": "erfunden"})
        enquiry.refresh_from_db()
        self.assertEqual(enquiry.status, "new")

    def test_the_totals_separate_what_is_open_from_what_is_won(self):
        rate = a_rate()
        an_enquiry(company="Nordwind GmbH", status="new", rate=rate)
        an_enquiry(company="Ostwerk", status="won", rate=rate, quantity=3)
        response = self.client.get("/studio/advertising/")
        self.assertEqual(response.context["open_value"], Decimal("900.00"))
        self.assertEqual(response.context["won_value"], Decimal("2700.00"))
        self.assertEqual(response.context["counts"]["open"], 1)
        self.assertEqual(response.context["counts"]["won"], 1)

    def test_an_enquiry_with_no_lines_still_reads(self):
        an_enquiry()
        self.assertEqual(self.client.get("/studio/advertising/").status_code, 200)

    def test_the_empty_inbox_says_so(self):
        self.assertContains(self.client.get("/studio/advertising/"), "empty-state")


class RateCardPageTests(Staff):
    def test_the_page_lists_what_is_for_sale_with_its_price(self):
        a_rate(price="1200.00", channel="print")
        response = self.client.get("/studio/advertising/rate-card/")
        self.assertContains(response, "Ganze Seite")
        self.assertContains(response, "1200")

    def test_a_slug_is_made_from_the_german_name(self):
        self.client.post("/studio/advertising/rate-card/", {
            "action": "save", "channel": "print", "slug": "", "name_de": "Halbe Seite",
            "price": "500", "unit": "edition", "order": 0, "is_active": "on",
        })
        self.assertEqual(RateCard.objects.get(name_de="Halbe Seite").slug, "halbe-seite")

    def test_a_size_needs_both_measurements(self):
        response = self.client.post("/studio/advertising/rate-card/", {
            "action": "save", "channel": "print", "slug": "", "name_de": "Anzeige",
            "price": "100", "unit": "edition", "order": 0, "width": 210, "height": "",
        })
        self.assertIn("height", response.context["form"].errors)
        self.assertFalse(RateCard.objects.exists())

    def test_an_entry_can_be_switched_off_without_losing_it(self):
        entry = a_rate()
        self.client.post("/studio/advertising/rate-card/", {"action": "toggle", "pk": entry.pk})
        entry.refresh_from_db()
        self.assertFalse(entry.is_active)
        self.assertTrue(RateCard.objects.filter(pk=entry.pk).exists())


class MediaKitPageTests(Staff):
    def test_a_kit_can_be_uploaded_and_is_listed(self):
        self.client.post("/studio/advertising/media-kits/", {
            "action": "save", "title": "Mediadaten", "year": 2026, "is_active": "on", "file": a_file(),
        })
        self.assertTrue(MediaKit.objects.filter(title="Mediadaten").exists())
        response = self.client.get("/studio/advertising/media-kits/")
        self.assertContains(response, "Mediadaten")
        self.assertContains(response, "2026")

    def test_the_newest_active_kit_is_the_one_offered(self):
        MediaKit.objects.create(title="Alt", year=2024, file=a_file("alt.pdf"))
        current = MediaKit.objects.create(title="Neu", year=2026, file=a_file("neu.pdf"))
        self.assertEqual(MediaKit.current(), current)

    def test_a_switched_off_kit_is_not_offered(self):
        MediaKit.objects.create(title="Zurückgezogen", year=2026, file=a_file(), is_active=False)
        self.assertIsNone(MediaKit.current())
