"""Language routing, RTL and the design-system page."""

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse


class LanguageTests(TestCase):
    def test_default_language_is_unprefixed_german(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<html lang="de" dir="ltr"')

    def test_arabic_prefix_renders_rtl(self):
        response = self.client.get("/ar/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<html lang="ar" dir="rtl"')

    def test_english_prefix(self):
        self.assertContains(self.client.get("/en/"), '<html lang="en" dir="ltr"')

    def test_language_switcher_redirects_to_prefixed_path(self):
        response = self.client.post(reverse("set_language"), {"language": "ar", "next": "/about/"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].startswith("/ar/"))

    def test_fonts_are_self_hosted(self):
        response = self.client.get("/")
        self.assertNotContains(response, "fonts.googleapis.com")
        self.assertContains(response, "js/vendor/gsap.min.js")


class StyleGuideTests(TestCase):
    @override_settings(DEBUG=False)
    def test_hidden_from_anonymous_when_not_debug(self):
        self.assertEqual(self.client.get(reverse("styleguide")).status_code, 302)

    @override_settings(DEBUG=False)
    def test_staff_can_open_it(self):
        user = get_user_model().objects.create_user(email="s@example.com", password="a-long-passw0rd!", is_staff=True)
        self.client.force_login(user)
        response = self.client.get(reverse("styleguide"))
        self.assertContains(response, "Everything in the project, on one page")
        self.assertContains(response, 'data-motion="stagger"')
