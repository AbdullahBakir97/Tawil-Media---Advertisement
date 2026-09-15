from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils.translation import activate
from PIL import Image

from source.apps.studio.models import PressAsset, PressKit, Theme


def an_image(name="logo.png"):
    buffer = BytesIO()
    Image.new("RGB", (400, 120), (11, 37, 69)).save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


class PressKitModelTests(TestCase):
    def test_only_one_kit_is_in_force(self):
        first = PressKit.objects.create(name="2025", is_current=True)
        second = PressKit.objects.create(name="2026", is_current=True)
        first.refresh_from_db()
        self.assertFalse(first.is_current)
        self.assertEqual(PressKit.current(), second)

    def test_there_is_no_kit_until_one_is_entered(self):
        self.assertIsNone(PressKit.current())

    def test_the_boilerplate_and_role_read_in_the_visitors_language(self):
        kit = PressKit.objects.create(
            boilerplate_de="Almadina erscheint in Berlin.",
            boilerplate_ar="تصدر المدينة في برلين.",
            contact_role_de="Pressesprecherin",
        )
        activate("de")
        self.assertEqual(kit.boilerplate, "Almadina erscheint in Berlin.")
        self.assertEqual(kit.contact_role, "Pressesprecherin")
        activate("ar")
        self.assertEqual(kit.boilerplate, "تصدر المدينة في برلين.")
        activate("de")


class PressAssetTests(TestCase):
    def setUp(self):
        self.kit = PressKit.objects.create(name="Kit")

    def test_a_web_image_is_its_own_thumbnail(self):
        asset = PressAsset.objects.create(kit=self.kit, label="Logo", file=an_image())
        self.assertEqual(asset.thumbnail, asset.file)
        self.assertEqual(asset.extension, "PNG")

    def test_a_file_a_browser_cannot_draw_needs_a_preview(self):
        asset = PressAsset.objects.create(
            kit=self.kit, label="Logo, vector",
            file=SimpleUploadedFile("logo.eps", b"%!PS-Adobe", content_type="application/postscript"),
        )
        self.assertIsNone(asset.thumbnail)
        self.assertEqual(asset.extension, "EPS")

        asset.preview = an_image("preview.png")
        asset.save()
        self.assertEqual(asset.thumbnail, asset.preview)


class PressPageTests(TestCase):
    def setUp(self):
        self.kit = PressKit.objects.create(
            boilerplate_de="Almadina ist die erste arabischsprachige Zeitschrift in Deutschland.",
            contact_name="A. Muster",
            contact_role_de="Pressesprecherin",
            contact_email="presse@example.com",
        )
        PressAsset.objects.create(kit=self.kit, label="Wortmarke", file=an_image(), background="light")
        PressAsset.objects.create(kit=self.kit, label="Wortmarke invertiert", file=an_image("logo-dark.png"),
                                  background="dark")

    def test_the_page_is_public(self):
        self.assertEqual(self.client.get("/press/").status_code, 200)

    def test_it_carries_the_boilerplate_and_the_contact(self):
        response = self.client.get("/press/")
        self.assertContains(response, "erste arabischsprachige Zeitschrift")
        self.assertContains(response, "A. Muster")
        self.assertContains(response, "presse@example.com")

    def test_assets_are_listed_with_the_background_they_belong_on(self):
        response = self.client.get("/press/")
        self.assertContains(response, "press-asset--light")
        self.assertContains(response, "press-asset--dark")
        self.assertContains(response, "Wortmarke")

    def test_the_palette_comes_from_the_default_theme(self):
        Theme.objects.create(name="Haus", slug="haus", accent="#ff0000", brand="#000080", is_default=True)
        response = self.client.get("/press/")
        self.assertContains(response, "#ff0000")
        self.assertContains(response, "#000080")

    def test_the_page_works_before_anything_is_entered(self):
        PressKit.objects.all().delete()
        response = self.client.get("/press/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "empty-state")
        self.assertContains(response, "Kontaktformular")

    def test_the_download_is_offered_only_when_there_is_one(self):
        self.assertNotContains(self.client.get("/press/"), "press/kit.zip")
        self.kit.archive = "press/kit.zip"
        self.kit.save()
        self.assertContains(self.client.get("/press/"), "press/kit.zip")
