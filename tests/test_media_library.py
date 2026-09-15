import shutil
import tempfile
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template import Context, Template
from django.test import TestCase, override_settings
from PIL import Image

from source.apps.content.imaging import measure, rendition, srcset
from source.apps.content.models import Media
from source.apps.studio.forms import MediaUploadForm

TEMP_MEDIA = tempfile.mkdtemp(prefix="media-library-tests-")


def an_image(name="cover.jpg", size=(1600, 1000), colour=(200, 120, 40)):
    buffer = BytesIO()
    Image.new("RGB", size, colour).save(buffer, format="JPEG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/jpeg")


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class MediaModelTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)
        super().tearDownClass()

    def test_uploading_an_image_records_its_size(self):
        item = Media.objects.create(file=an_image(), media_type="image")
        self.assertEqual((item.width, item.height), (1600, 1000))
        self.assertEqual(item.aspect_ratio, "1600 / 1000")

    def test_a_file_that_is_not_an_image_keeps_no_size(self):
        item = Media.objects.create(
            file=SimpleUploadedFile("notes.pdf", b"%PDF-1.4 not really", content_type="application/pdf"),
            media_type="document",
        )
        self.assertIsNone(item.width)
        self.assertIsNone(item.aspect_ratio)
        self.assertFalse(item.is_image)

    def test_the_focal_point_becomes_a_css_object_position(self):
        item = Media.objects.create(file=an_image(), media_type="image", focal_x=0.25, focal_y=0.8)
        self.assertEqual(item.object_position, "25% 80%")

    def test_measure_returns_nothing_for_an_unreadable_file(self):
        item = Media.objects.create(
            file=SimpleUploadedFile("broken.jpg", b"not an image", content_type="image/jpeg"), media_type="image"
        )
        self.assertIsNone(measure(item.file))


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class RenditionTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)
        super().tearDownClass()

    def test_a_rendition_is_built_once_and_reused(self):
        item = Media.objects.create(file=an_image(), media_type="image")
        first = rendition(item, 800)
        self.assertTrue(first.endswith(".webp"))
        self.assertEqual(rendition(item, 800), first)

    def test_no_rendition_is_built_wider_than_the_source(self):
        item = Media.objects.create(file=an_image(size=(600, 400)), media_type="image")
        self.assertIsNone(rendition(item, 1200))

    def test_srcset_lists_the_smaller_sizes_and_the_original(self):
        item = Media.objects.create(file=an_image(size=(1200, 800)), media_type="image")
        value = srcset(item)
        self.assertIn("400w", value)
        self.assertIn("800w", value)
        self.assertNotIn("1600w", value)
        self.assertIn(item.file.url, value)

    def test_a_document_never_gets_a_rendition(self):
        item = Media.objects.create(
            file=SimpleUploadedFile("kit.pdf", b"%PDF-1.4", content_type="application/pdf"), media_type="document"
        )
        self.assertIsNone(rendition(item, 800))
        self.assertEqual(srcset(item), "")


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class PictureTagTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)
        super().tearDownClass()

    def render(self, media, extra=""):
        template = Template("{% load media_tags %}{% picture item " + extra + " %}")
        return template.render(Context({"item": media}))

    def test_the_tag_renders_dimensions_and_a_srcset(self):
        item = Media.objects.create(file=an_image(), media_type="image", alt_text="Der Hafen")
        html = self.render(item)
        self.assertIn('width="1600" height="1000"', html)
        self.assertIn('alt="Der Hafen"', html)
        self.assertIn("srcset=", html)
        self.assertIn('loading="lazy"', html)

    def test_the_focal_point_is_applied_only_when_it_is_off_centre(self):
        centred = Media.objects.create(file=an_image(), media_type="image")
        self.assertNotIn("object-position", self.render(centred))
        off = Media.objects.create(file=an_image("side.jpg"), media_type="image", focal_x=0.2, focal_y=0.3)
        self.assertIn("object-position:20% 30%", self.render(off))

    def test_the_alt_text_is_escaped(self):
        item = Media.objects.create(file=an_image(), media_type="image", alt_text='<script>"x"')
        html = self.render(item)
        self.assertNotIn("<script>", html)

    def test_nothing_is_rendered_without_a_picture(self):
        self.assertEqual(self.render(None), "")


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class MediaLibraryViewTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.staff = get_user_model().objects.create_user(
            email="desk@example.com", password="pw-for-tests", is_staff=True
        )
        self.item = Media.objects.create(file=an_image(), media_type="image", alt_text="Hafen")

    def test_the_library_is_staff_only(self):
        self.assertEqual(self.client.get("/studio/media/").status_code, 302)
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get("/studio/media/").status_code, 200)

    def test_details_are_saved_and_the_focal_point_is_clamped(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            "/studio/media/",
            {"pk": self.item.pk, "alt_text": "Der Hafen", "caption": "Am Morgen", "credit": "A. Muster",
             "focal_x": "1.8", "focal_y": "-0.4"},
        )
        self.assertEqual(response.status_code, 302)
        self.item.refresh_from_db()
        self.assertEqual(self.item.alt_text, "Der Hafen")
        self.assertEqual(self.item.caption, "Am Morgen")
        self.assertEqual((self.item.focal_x, self.item.focal_y), (1.0, 0.0))

    def test_uploading_sorts_files_into_types(self):
        self.client.force_login(self.staff)
        self.client.post(
            "/studio/media/",
            {"action": "upload", "files": [an_image("neu.jpg"),
                                           SimpleUploadedFile("kit.pdf", b"%PDF-1.4", content_type="application/pdf")]},
        )
        self.assertEqual(Media.objects.get(file__endswith="neu.jpg").media_type, "image")
        self.assertEqual(Media.objects.get(file__contains="kit").media_type, "document")

    def test_the_search_filters_the_grid(self):
        Media.objects.create(file=an_image("berlin.jpg"), media_type="image", alt_text="Berlin bei Nacht")
        self.client.force_login(self.staff)
        response = self.client.get("/studio/media/?q=Berlin")
        self.assertContains(response, "Berlin bei Nacht")
        self.assertNotContains(response, "Hafen</span>")

    def test_a_file_can_be_deleted(self):
        self.client.force_login(self.staff)
        self.client.post("/studio/media/", {"pk": self.item.pk, "action": "delete"})
        self.assertFalse(Media.objects.filter(pk=self.item.pk).exists())

    def test_the_upload_form_reads_the_type_from_the_name(self):
        self.assertEqual(MediaUploadForm.kind("a.PNG"), "image")
        self.assertEqual(MediaUploadForm.kind("clip.mp4"), "video")
        self.assertEqual(MediaUploadForm.kind("rates"), "document")
