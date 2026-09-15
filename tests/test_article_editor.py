from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils.translation import activate
from PIL import Image

from source.apps.content.models import Article, Category, Media


def an_image(name="bild.png"):
    buffer = BytesIO()
    Image.new("RGB", (120, 80), (11, 37, 69)).save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


def staff():
    return get_user_model().objects.create_user(email="desk@example.com", password="pw-for-tests", is_staff=True)


class ArticleTranslationTests(TestCase):
    def setUp(self):
        self.article = Article.objects.create(title="Die Stadt am Morgen", content="Ein Text über Berlin.")

    def tearDown(self):
        activate("de")

    def test_a_reader_sees_the_desk_wording_until_a_translation_exists(self):
        self.assertEqual(self.article.label, "Die Stadt am Morgen")
        self.assertEqual(self.article.body, "Ein Text über Berlin.")

    def test_each_language_replaces_it_once_written(self):
        self.article.title_ar = "المدينة في الصباح"
        self.article.content_ar = "نص عن برلين."
        self.article.save()

        activate("ar")
        self.assertEqual(self.article.label, "المدينة في الصباح")
        self.assertEqual(self.article.body, "نص عن برلين.")

        activate("en")
        self.assertEqual(self.article.label, "Die Stadt am Morgen")

    def test_the_standfirst_is_used_when_written_and_derived_when_not(self):
        self.assertIn("Ein Text über Berlin", self.article.excerpt)

        self.article.standfirst_de = "Was die Stadt bei Sonnenaufgang erzählt."
        self.article.save()
        self.assertEqual(self.article.excerpt, "Was die Stadt bei Sonnenaufgang erzählt.")

    def test_reading_time_counts_the_language_the_reader_gets(self):
        self.article.content_ar = " ".join(["كلمة"] * 600)
        self.article.save()
        activate("ar")
        self.assertEqual(self.article.reading_time, 3)
        activate("de")
        self.assertEqual(self.article.reading_time, 1)

    def test_the_desk_title_is_what_staff_see(self):
        self.article.title_ar = "المدينة"
        self.article.save()
        activate("ar")
        self.assertEqual(str(self.article), "Die Stadt am Morgen")


class ArticleSearchTests(TestCase):
    def setUp(self):
        self.article = Article.objects.create(
            title="Die Stadt am Morgen",
            content="Ein Text über Berlin.",
            title_ar="المدينة في الصباح",
            content_ar="نص عن برلين وحياتها.",
        )
        self.article.go_live()

    def test_searching_in_arabic_finds_the_arabic_headline(self):
        response = self.client.get("/search/?q=المدينة")
        self.assertContains(response, "المدينة")
        self.assertEqual(list(response.context["object_list"]), [self.article])

    def test_searching_the_arabic_body_finds_it_too(self):
        response = self.client.get("/search/?q=وحياتها")
        self.assertEqual(list(response.context["object_list"]), [self.article])

    def test_the_desk_wording_is_still_searchable(self):
        response = self.client.get("/search/?q=Morgen")
        self.assertEqual(list(response.context["object_list"]), [self.article])

    def test_suggestions_match_a_term_in_any_language(self):
        """The search reaches every language; the dropdown still shows the
        headline in the one the reader is browsing in."""
        self.assertContains(self.client.get("/search/suggestions/?q=المدينة"), "Die Stadt am Morgen")
        self.assertContains(self.client.get("/ar/search/suggestions/?q=المدينة"), "المدينة في الصباح")


class ArticleEditorTests(TestCase):
    def setUp(self):
        self.user = staff()
        self.client.force_login(self.user)
        self.category = Category.objects.create(name="Politik", slug="politik")

    def form_data(self, **overrides):
        data = {
            "title": "Die Stadt am Morgen",
            "slug": "",
            "content": "Ein Text über Berlin.",
            "title_de": "", "title_ar": "", "title_en": "",
            "standfirst_de": "", "standfirst_ar": "", "standfirst_en": "",
            "content_de": "", "content_ar": "", "content_en": "",
            "author": self.user.pk,
            "categories": [self.category.pk],
            "tags": "",
            "action": "save",
        }
        data.update(overrides)
        return data

    def test_the_editor_is_staff_only(self):
        self.client.logout()
        self.assertEqual(self.client.get("/studio/articles/new/").status_code, 302)

    def test_a_new_article_can_be_written_and_starts_as_a_draft(self):
        response = self.client.post("/studio/articles/new/", self.form_data())
        article = Article.objects.get(title="Die Stadt am Morgen")
        self.assertRedirects(response, f"/studio/articles/{article.pk}/")
        self.assertEqual(article.status, "draft")
        self.assertFalse(article.is_published)
        self.assertEqual(article.slug, "die-stadt-am-morgen")
        self.assertEqual(list(article.categories.all()), [self.category])

    def test_saving_an_article_never_publishes_it(self):
        article = Article.objects.create(title="Entwurf", content="x")
        self.client.post(f"/studio/articles/{article.pk}/", self.form_data(title="Entwurf geändert"))
        article.refresh_from_db()
        self.assertEqual(article.status, "draft")
        self.assertFalse(article.is_published)
        self.assertEqual(article.title, "Entwurf geändert")

    def test_saving_a_live_article_keeps_it_live(self):
        article = Article.objects.create(title="Live", content="x")
        article.go_live()
        self.client.post(f"/studio/articles/{article.pk}/", self.form_data(title="Live, korrigiert"))
        article.refresh_from_db()
        self.assertTrue(article.is_published)
        self.assertEqual(article.title, "Live, korrigiert")

    def test_save_and_send_to_review_moves_it_along(self):
        self.client.post("/studio/articles/new/", self.form_data(action="save-and-review"))
        self.assertEqual(Article.objects.get(title="Die Stadt am Morgen").status, "review")

    def test_translations_are_written_from_the_editor(self):
        self.client.post("/studio/articles/new/", self.form_data(title_ar="المدينة", content_ar="نص"))
        article = Article.objects.get(title="Die Stadt am Morgen")
        self.assertEqual(article.title_ar, "المدينة")
        activate("ar")
        self.assertEqual(article.label, "المدينة")
        activate("de")

    def test_a_sponsored_piece_must_name_its_sponsor(self):
        response = self.client.post("/studio/articles/new/", self.form_data(is_sponsored="on", sponsor_name=""))
        self.assertEqual(response.status_code, 200)
        # Assert the error itself rather than its wording, which is translated.
        self.assertIn("sponsor_name", response.context["form"].errors)
        self.assertFalse(Article.objects.exists())

    def test_a_sponsored_piece_with_a_sponsor_saves(self):
        self.client.post("/studio/articles/new/", self.form_data(is_sponsored="on", sponsor_name="Beispiel GmbH"))
        article = Article.objects.get(title="Die Stadt am Morgen")
        self.assertTrue(article.is_sponsored)
        self.assertEqual(article.sponsor_name, "Beispiel GmbH")

    def test_an_article_can_be_deleted_from_the_editor(self):
        article = Article.objects.create(title="Weg damit", content="x")
        response = self.client.post(f"/studio/articles/{article.pk}/", {"action": "delete"})
        self.assertRedirects(response, "/studio/desk/")
        self.assertFalse(Article.objects.filter(pk=article.pk).exists())

    def test_the_editor_opens_an_existing_article_with_its_text(self):
        article = Article.objects.create(title="Bestehend", content="Der Text.", title_ar="قائم")
        response = self.client.get(f"/studio/articles/{article.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bestehend")
        self.assertContains(response, "Der Text.")
        self.assertContains(response, "قائم")

    def test_the_desk_links_each_article_to_its_editor(self):
        article = Article.objects.create(title="Auf dem Desk", content="x")
        self.assertContains(self.client.get("/studio/desk/"), f"/studio/articles/{article.pk}/")

    def test_a_picture_can_actually_be_attached(self):
        """The picker limits how many pictures it offers; that limit must not
        make every choice invalid when the form is submitted."""
        picture = Media.objects.create(alt_text="Ein Bild", media_type="image", file=an_image())
        self.client.post("/studio/articles/new/", self.form_data(media=[picture.pk]))
        article = Article.objects.get(title="Die Stadt am Morgen")
        self.assertEqual(list(article.media.all()), [picture])
        self.assertEqual(article.cover, picture)

    def test_only_pictures_are_offered_as_attachments(self):
        picture = Media.objects.create(alt_text="Ein Bild", media_type="image", file=an_image())
        video = Media.objects.create(alt_text="Ein Video", media_type="video",
                                     file=SimpleUploadedFile("video.mp4", b"not-really-a-video"))
        html = self.client.get("/studio/articles/new/").content.decode()
        # Stored names get a suffix when the file already exists, so match the
        # checkbox values rather than the file names.
        self.assertIn(f'name="media" value="{picture.pk}"', html)
        self.assertNotIn(f'name="media" value="{video.pk}"', html)
