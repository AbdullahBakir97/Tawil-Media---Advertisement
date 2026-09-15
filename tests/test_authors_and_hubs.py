from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils.translation import activate

from source.apps.content.models import Article, Category, Contributor


def an_article(author=None, categories=(), **kwargs):
    kwargs.setdefault("title", "Die Stadt am Morgen")
    kwargs.setdefault("content", "Ein Text über Berlin. " * 20)
    article = Article.objects.create(author=author, **kwargs)
    article.categories.set(categories)
    return article.go_live()


class CategoryLabelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Culture", slug="culture", description="Fallback intro")

    def test_the_desk_label_is_used_until_a_translation_exists(self):
        self.assertEqual(self.category.label, "Culture")
        self.assertEqual(self.category.intro, "Fallback intro")

    def test_the_visitors_language_wins_when_it_is_written(self):
        self.category.name_de, self.category.intro_de = "Kultur", "Was in Berlin gespielt wird."
        self.category.name_ar = "ثقافة"
        self.category.save()
        activate("de")
        self.assertEqual(self.category.label, "Kultur")
        self.assertEqual(self.category.intro, "Was in Berlin gespielt wird.")
        activate("ar")
        self.assertEqual(self.category.label, "ثقافة")
        activate("de")


class CategoryHubTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Culture", slug="culture", name_de="Kultur", accent="#f2b25c")
        self.other = Category.objects.create(name="Politics", slug="politics", name_de="Politik")
        self.lead = an_article(title="Erste Geschichte", slug="erste", categories=[self.category])
        self.second = an_article(title="Zweite Geschichte", slug="zweite", categories=[self.category])
        an_article(title="Andere Rubrik", slug="andere", categories=[self.other])

    def test_the_hub_has_its_own_template_and_header(self):
        response = self.client.get("/articles/category/culture/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "content/category_hub.html")
        self.assertContains(response, "hub-hero")
        self.assertContains(response, "Kultur")

    def test_the_accent_colours_the_header(self):
        self.assertContains(self.client.get("/articles/category/culture/"), "--hub-accent: #f2b25c")

    def test_only_this_sections_articles_appear(self):
        response = self.client.get("/articles/category/culture/")
        listed = {article.title for article in response.context["articles"]}
        self.assertEqual(listed, {"Erste Geschichte", "Zweite Geschichte"})
        self.assertContains(response, "Erste Geschichte")

    def test_the_neighbouring_sections_are_offered(self):
        self.assertContains(self.client.get("/articles/category/culture/"), "Politik")

    def test_the_plain_list_is_untouched(self):
        response = self.client.get("/articles/")
        self.assertTemplateUsed(response, "content/article_list.html")

    def test_an_empty_section_says_so(self):
        Category.objects.create(name="Sport", slug="sport")
        response = self.client.get("/articles/category/sport/")
        self.assertContains(response, "empty-state")


class ContributorTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="leila@example.com", password="pw-for-tests", first_name="Leila", last_name="Haddad"
        )
        self.contributor = Contributor.objects.create(
            name="Leila Haddad", user=self.user, role_de="Reporterin", bio_de="Schreibt über Berlin."
        )

    def test_the_slug_is_made_from_the_name(self):
        self.assertEqual(self.contributor.slug, "leila-haddad")

    def test_initials_fall_back_to_two_letters(self):
        self.assertEqual(self.contributor.initials, "LH")
        self.assertEqual(Contributor.objects.create(name="Amir").initials, "A")

    def test_the_role_and_bio_read_in_the_visitors_language(self):
        activate("de")
        self.assertEqual(self.contributor.role, "Reporterin")
        self.assertEqual(self.contributor.bio, "Schreibt über Berlin.")

    def test_only_published_articles_by_this_person_are_listed(self):
        mine = an_article(author=self.user, slug="meine")
        Article.objects.create(title="Entwurf", slug="entwurf", content="x", author=self.user)
        other = get_user_model().objects.create_user(email="other@example.com", password="pw-for-tests")
        an_article(author=other, title="Fremd", slug="fremd")
        self.assertEqual(list(self.contributor.articles()), [mine])

    def test_a_contributor_without_an_account_has_no_articles(self):
        guest = Contributor.objects.create(name="Gastautor")
        self.assertEqual(list(guest.articles()), [])

    def test_the_team_page_lists_active_contributors_only(self):
        Contributor.objects.create(name="Ehemalig", is_active=False)
        response = self.client.get("/authors/")
        self.assertContains(response, "Leila Haddad")
        self.assertNotContains(response, "Ehemalig")

    def test_the_writers_page_shows_the_bio_and_the_work(self):
        an_article(author=self.user, title="Nachts am Kanal", slug="nachts")
        response = self.client.get("/authors/leila-haddad/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Leila Haddad")
        self.assertContains(response, "Reporterin")
        self.assertContains(response, "Nachts am Kanal")

    def test_a_hidden_contributor_has_no_page(self):
        Contributor.objects.create(name="Ehemalig", slug="ehemalig", is_active=False)
        self.assertEqual(self.client.get("/authors/ehemalig/").status_code, 404)

    def test_a_writer_with_nothing_published_says_so(self):
        self.assertContains(self.client.get("/authors/leila-haddad/"), "empty-state")


class BylineTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="leila@example.com", password="pw-for-tests", first_name="Leila", last_name="Haddad"
        )

    def test_a_byline_links_to_the_writers_page(self):
        Contributor.objects.create(name="Leila Haddad", user=self.user)
        an_article(author=self.user, slug="mit-seite")
        self.assertContains(self.client.get("/articles/mit-seite/"), "/authors/leila-haddad/")

    def test_a_byline_without_a_page_is_plain_text(self):
        article = an_article(author=self.user, slug="ohne-seite")
        self.assertIsNone(article.byline)
        self.assertEqual(article.byline_name, "Leila Haddad")
        response = self.client.get("/articles/ohne-seite/")
        self.assertContains(response, "Leila Haddad")
        # The name is plain text in the byline; only the site nav links to /authors/.
        self.assertNotContains(response, 'class="byline"')

    @override_settings(LANGUAGE_CODE="de")
    def test_an_article_without_an_author_has_no_byline(self):
        article = an_article(slug="ohne-autor")
        self.assertIsNone(article.byline)
        self.assertEqual(article.byline_name, "")
