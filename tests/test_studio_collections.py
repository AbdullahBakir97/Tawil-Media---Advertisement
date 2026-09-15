from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from source.apps.content.models import Article, Magazine, Media
from source.apps.studio.models import FAQ, AdSlot, Milestone, Partner, Testimonial


def an_image(name="logo.png"):
    buffer = BytesIO()
    Image.new("RGB", (80, 60), (11, 37, 69)).save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


class StudioPagesTests(TestCase):
    """Every nav entry is a Studio page now, not a jump into the admin."""

    PAGES = ["/studio/ad-slots/", "/studio/partners/", "/studio/voices/",
             "/studio/faq/", "/studio/timeline/", "/studio/editions/"]

    def setUp(self):
        self.client.force_login(
            get_user_model().objects.create_user(email="desk@example.com", password="pw-for-tests", is_staff=True)
        )

    def test_every_page_opens(self):
        for url in self.PAGES:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_every_page_is_staff_only(self):
        self.client.logout()
        for url in self.PAGES:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 302)

    def test_the_studio_no_longer_links_into_the_django_admin(self):
        html = self.client.get("/studio/").content.decode()
        self.assertNotIn("/admin/studio/", html)
        self.assertNotIn("/admin/content/", html)


class CollectionBehaviourTests(TestCase):
    """The shared collection view, exercised through the partners page."""

    def setUp(self):
        self.client.force_login(
            get_user_model().objects.create_user(email="desk@example.com", password="pw-for-tests", is_staff=True)
        )

    def add(self, name, **extra):
        data = {"action": "save", "name": name, "url": "https://example.com", "order": 0, "is_active": "on"}
        data.update(extra)
        return self.client.post("/studio/partners/", {**data, "logo": an_image()})

    def test_a_row_can_be_added(self):
        self.add("Beispiel GmbH")
        self.assertTrue(Partner.objects.filter(name="Beispiel GmbH").exists())

    def test_a_row_can_be_edited_in_place(self):
        self.add("Falsch")
        partner = Partner.objects.get()
        response = self.client.get(f"/studio/partners/?edit={partner.pk}")
        self.assertContains(response, "Falsch")
        self.assertContains(response, "is-editing")

        self.client.post("/studio/partners/", {"action": "save", "pk": partner.pk, "name": "Richtig",
                                               "url": "https://example.com", "order": 0, "is_active": "on"})
        partner.refresh_from_db()
        self.assertEqual(partner.name, "Richtig")

    def test_a_row_is_switched_off_rather_than_deleted(self):
        self.add("Beispiel")
        partner = Partner.objects.get()
        self.client.post("/studio/partners/", {"action": "toggle", "pk": partner.pk})
        partner.refresh_from_db()
        self.assertFalse(partner.is_active)
        self.assertTrue(Partner.objects.filter(pk=partner.pk).exists())

        self.client.post("/studio/partners/", {"action": "toggle", "pk": partner.pk})
        partner.refresh_from_db()
        self.assertTrue(partner.is_active)

    def test_a_row_can_be_deleted(self):
        self.add("Weg damit")
        partner = Partner.objects.get()
        self.client.post("/studio/partners/", {"action": "delete", "pk": partner.pk})
        self.assertFalse(Partner.objects.exists())

    def test_rows_can_be_reordered(self):
        first = Partner.objects.create(name="Erster", logo=an_image(), order=0)
        second = Partner.objects.create(name="Zweiter", logo=an_image(), order=1)
        self.client.post("/studio/partners/", {"action": "move", "pk": second.pk, "direction": "up"})
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertEqual(second.order, 0)
        self.assertEqual(first.order, 1)

    def test_moving_the_top_row_up_does_nothing(self):
        top = Partner.objects.create(name="Erster", logo=an_image(), order=0)
        Partner.objects.create(name="Zweiter", logo=an_image(), order=1)
        self.client.post("/studio/partners/", {"action": "move", "pk": top.pk, "direction": "up"})
        top.refresh_from_db()
        self.assertEqual(top.order, 0)

    def test_a_new_row_goes_to_the_end(self):
        Partner.objects.create(name="Erster", logo=an_image(), order=0)
        Partner.objects.create(name="Zweiter", logo=an_image(), order=1)
        self.add("Dritter")
        self.assertEqual(Partner.objects.get(name="Dritter").order, 2)

    def test_an_invalid_form_says_so_and_saves_nothing(self):
        response = self.client.post("/studio/partners/", {"action": "save", "name": "", "order": 0})
        self.assertEqual(response.status_code, 200)
        self.assertIn("name", response.context["form"].errors)
        self.assertFalse(Partner.objects.exists())


class AdSlotPageTests(TestCase):
    def setUp(self):
        self.client.force_login(
            get_user_model().objects.create_user(email="desk@example.com", password="pw-for-tests", is_staff=True)
        )

    def test_a_booking_must_end_after_it_starts(self):
        response = self.client.post("/studio/ad-slots/", {
            "action": "save", "key": "home-leaderboard", "format": "leaderboard", "weight": 1,
            "image": an_image(), "starts_at": "2026-10-01T10:00", "ends_at": "2026-09-01T10:00",
        })
        self.assertIn("ends_at", response.context["form"].errors)
        self.assertFalse(AdSlot.objects.exists())

    def test_a_slot_lists_its_key_and_format(self):
        AdSlot.objects.create(key="home-leaderboard", advertiser="Beispiel GmbH", image=an_image())
        response = self.client.get("/studio/ad-slots/")
        self.assertContains(response, "Beispiel GmbH")
        self.assertContains(response, "home-leaderboard")


class OtherCollectionsTests(TestCase):
    def setUp(self):
        self.client.force_login(
            get_user_model().objects.create_user(email="desk@example.com", password="pw-for-tests", is_staff=True)
        )

    def test_a_voice_is_listed_by_its_name_and_role(self):
        Testimonial.objects.create(quote_de="Ein gutes Heft.", name="A. Muster", role="Leserin")
        response = self.client.get("/studio/voices/")
        self.assertContains(response, "A. Muster")
        self.assertContains(response, "Leserin")

    def test_a_question_is_listed_with_the_page_it_belongs_to(self):
        FAQ.objects.create(page="help", question_de="Wie abonniere ich?", answer_de="So.")
        self.assertContains(self.client.get("/studio/faq/"), "Wie abonniere ich?")

    def test_a_milestone_is_listed_by_its_year(self):
        Milestone.objects.create(year=2019, title_de="Gegründet")
        response = self.client.get("/studio/timeline/")
        self.assertContains(response, "Gegründet")
        self.assertContains(response, "2019")

    def test_milestones_read_in_year_order(self):
        Milestone.objects.create(year=2024, title_de="Später")
        Milestone.objects.create(year=2019, title_de="Früher")
        rows = self.client.get("/studio/timeline/").content.decode()
        self.assertLess(rows.index("Früher"), rows.index("Später"))


class MagazineEditorTests(TestCase):
    def setUp(self):
        self.client.force_login(
            get_user_model().objects.create_user(email="desk@example.com", password="pw-for-tests", is_staff=True)
        )

    def test_the_list_shows_every_edition(self):
        Magazine.objects.create(title="Ausgabe 13", slug="ausgabe-13", issue_number=13)
        response = self.client.get("/studio/editions/")
        self.assertContains(response, "Ausgabe 13")

    def test_an_edition_can_be_created_and_starts_as_a_draft(self):
        self.client.post("/studio/editions/", {"title": "Ausgabe 14", "slug": "", "issue_number": 14,
                                               "description": "", "articles": []})
        edition = Magazine.objects.get(title="Ausgabe 14")
        self.assertEqual(edition.slug, "ausgabe-14")
        self.assertEqual(edition.status, "draft")
        self.assertFalse(edition.is_published)

    def test_saving_a_live_edition_keeps_it_live(self):
        edition = Magazine.objects.create(title="Live", slug="live")
        edition.go_live()
        self.client.post(f"/studio/editions/{edition.pk}/", {"title": "Live, korrigiert", "slug": "live",
                                                             "issue_number": "", "description": "", "articles": []})
        edition.refresh_from_db()
        self.assertTrue(edition.is_published)
        self.assertEqual(edition.title, "Live, korrigiert")

    def test_articles_can_be_put_into_an_edition(self):
        article = Article.objects.create(title="Ein Beitrag", content="x")
        article.go_live()
        edition = Magazine.objects.create(title="Ausgabe 15", slug="ausgabe-15")
        self.client.post(f"/studio/editions/{edition.pk}/", {"title": "Ausgabe 15", "slug": "ausgabe-15",
                                                             "issue_number": "", "description": "",
                                                             "articles": [article.pk]})
        self.assertEqual(list(edition.articles.all()), [article])

    def test_only_published_articles_are_offered(self):
        Article.objects.create(title="Noch ein Entwurf", content="x")
        response = self.client.get("/studio/editions/?new=1")
        self.assertNotContains(response, "Noch ein Entwurf")

    def test_an_edition_can_be_deleted(self):
        edition = Magazine.objects.create(title="Weg damit", slug="weg-damit")
        self.client.post(f"/studio/editions/{edition.pk}/", {"action": "delete"})
        self.assertFalse(Magazine.objects.filter(pk=edition.pk).exists())

    def test_a_cover_can_be_chosen_from_the_library(self):
        picture = Media.objects.create(alt_text="Titelbild", media_type="image", file=an_image())
        edition = Magazine.objects.create(title="Ausgabe 16", slug="ausgabe-16")
        self.client.post(f"/studio/editions/{edition.pk}/", {"title": "Ausgabe 16", "slug": "ausgabe-16",
                                                             "issue_number": "", "description": "",
                                                             "cover_image": picture.pk, "articles": []})
        edition.refresh_from_db()
        self.assertEqual(edition.cover_image, picture)
