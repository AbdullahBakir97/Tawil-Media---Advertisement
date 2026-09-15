from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from source.apps.content.models import Magazine
from source.apps.studio.models import Announcement, HeroConfig, MagazinePage, Theme

User = get_user_model()


class StudioAccessTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(email="staff@example.com", password="a-long-passw0rd!", is_staff=True)
        self.reader = User.objects.create_user(email="reader@example.com", password="a-long-passw0rd!")

    def test_studio_is_staff_only(self):
        for url in ("/studio/", "/studio/hero/", "/studio/themes/", "/studio/announcements/"):
            self.assertEqual(self.client.get(url).status_code, 302, url)
        self.client.force_login(self.reader)
        self.assertEqual(self.client.get("/studio/").status_code, 403)
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get("/studio/").status_code, 200)

    def test_hero_previews_are_framable_by_the_studio_only(self):
        self.client.force_login(self.staff)
        response = self.client.get("/studio/hero/preview/light/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-Frame-Options"], "SAMEORIGIN")
        self.assertEqual(self.client.get("/studio/").headers["X-Frame-Options"], "DENY")


class HeroConfigTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(email="staff@example.com", password="a-long-passw0rd!", is_staff=True)
        self.client.force_login(self.staff)

    def test_every_variant_renders_on_the_home_page(self):
        hero = HeroConfig.for_placement("home")
        for variant, _label in HeroConfig.VARIANTS:
            hero.variant = variant
            hero.save()
            response = self.client.get("/")
            self.assertEqual(response.status_code, 200, variant)
            self.assertContains(response, f"hero-root--{variant}")

    def test_saved_copy_reaches_the_page(self):
        hero = HeroConfig.for_placement("home")
        hero.headline_de = "Ein *goldenes* Wort"
        hero.dek_de = "Die Unterzeile aus dem Studio."
        hero.save()
        response = self.client.get("/")
        self.assertContains(response, "<em>goldenes</em>")
        self.assertContains(response, "Die Unterzeile aus dem Studio.")

    def test_headline_markup_is_escaped(self):
        hero = HeroConfig.for_placement("home")
        hero.headline_de = "<script>alert(1)</script> *x*"
        hero.save()
        response = self.client.get("/")
        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertContains(response, "&lt;script&gt;")


class AnnouncementTests(TestCase):
    def test_only_live_items_render(self):
        Announcement.objects.create(text_de="Sichtbar", kind="editorial")
        Announcement.objects.create(text_de="Abgelaufen", ends_at=timezone.now() - timezone.timedelta(days=1))
        Announcement.objects.create(text_de="Inaktiv", is_active=False)
        response = self.client.get("/")
        self.assertContains(response, "Sichtbar")
        self.assertNotContains(response, "Abgelaufen")
        self.assertNotContains(response, "Inaktiv")


class ThemeTests(TestCase):
    def test_default_theme_is_exclusive_and_sets_variables(self):
        first = Theme.objects.create(name="A", slug="a", is_default=True)
        second = Theme.objects.create(name="B", slug="b", accent="#ff0000", is_default=True)
        first.refresh_from_db()
        self.assertFalse(first.is_default)
        self.assertTrue(second.is_default)
        self.assertIn("--gold-400:#ff0000", second.css_vars())
        self.assertContains(self.client.get("/"), "--gold-400:#ff0000")


class ReaderTests(TestCase):
    def setUp(self):
        self.magazine = Magazine.objects.create(title="Edition One", slug="edition-one")
        self.magazine.publish()

    def test_reader_without_pages_explains_itself(self):
        response = self.client.get("/magazines/edition-one/read/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "reader-empty")

    def test_reader_lists_every_page(self):
        for number in range(1, 4):
            MagazinePage.objects.create(magazine=self.magazine, number=number, image=f"magazines/pages/p{number}.jpg")
        response = self.client.get("/magazines/edition-one/read/")
        self.assertContains(response, "reader-page", count=3)
        self.assertContains(response, "flipbook(")

    def test_unpublished_edition_has_no_reader(self):
        self.magazine.unpublish()
        self.assertEqual(self.client.get("/magazines/edition-one/read/").status_code, 404)
