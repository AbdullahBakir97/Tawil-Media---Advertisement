"""Every public page renders, and the auth flow works end to end."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from source.apps.content.models import Article, Category, Magazine

User = get_user_model()

PUBLIC_PAGES = [
    "home", "search", "sitemap", "about", "contact", "advertise", "careers",
    "help", "privacy", "terms", "cookies", "login", "register", "password_reset",
    "articles:list", "magazines:list", "archives:browse",
]


class PublicPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = User.objects.create_user(email="editor@example.com", password="s3cret-pass!", first_name="Ed", last_name="Itor")
        cls.category = Category.objects.create(name="News")
        cls.article = Article.objects.create(title="Hello world", content="Body text", author=author)
        cls.article.categories.add(cls.category)
        cls.article.tags.add("launch")
        cls.article.publish()
        cls.draft = Article.objects.create(title="Draft", content="Not yet", author=author)
        cls.magazine = Magazine.objects.create(title="Issue 1")
        cls.magazine.articles.add(cls.article)
        cls.magazine.publish()

    def test_every_public_page_renders(self):
        for name in PUBLIC_PAGES:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200, name)
                self.assertContains(response, "</html>")

    def test_home_lists_published_articles_only(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Hello world")
        self.assertNotContains(response, ">Draft<")

    def test_article_pages(self):
        self.assertEqual(self.client.get(reverse("articles:detail", args=[self.article.slug])).status_code, 200)
        self.assertEqual(self.client.get(reverse("articles:detail", args=[self.draft.slug])).status_code, 404)
        self.assertContains(self.client.get(reverse("articles:by_category", args=["news"])), "Hello world")
        self.assertContains(self.client.get(reverse("articles:by_tag", args=["launch"])), "Hello world")
        self.assertEqual(self.client.get(reverse("magazines:detail", args=[self.magazine.slug])).status_code, 200)

    def test_search(self):
        response = self.client.get(reverse("search"), {"q": "hello"})
        self.assertContains(response, "Hello world")
        response = self.client.get(reverse("search:suggestions"), {"q": "hel"})
        self.assertContains(response, "Hello world")

    def test_newsletter_subscribe(self):
        url = reverse("newsletter:subscribe")
        self.assertContains(self.client.post(url, {"email": "a@example.com"}), "Thanks")
        self.assertEqual(self.client.post(url, {"email": "nope"}).status_code, 400)

    def test_unknown_page_uses_custom_404(self):
        response = self.client.get("/definitely-not-here/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Diese Seite wurde nicht gefunden", status_code=404)
        english = self.client.get("/en/definitely-not-here/")
        self.assertContains(english, "couldn't find that page", status_code=404)


class AuthFlowTests(TestCase):
    def test_register_login_logout(self):
        response = self.client.post(reverse("register"), {
            "email": "New@Example.com", "first_name": "New", "last_name": "User",
            "password": "a-long-passw0rd!", "phone": "123",
        })
        self.assertRedirects(response, reverse("profile"))
        user = User.objects.get(email="new@example.com")
        self.assertTrue(user.check_password("a-long-passw0rd!"))
        self.assertTrue(user.username)

        self.client.post(reverse("logout"))
        self.assertEqual(self.client.get(reverse("profile")).status_code, 302)

        response = self.client.post(reverse("login"), {"email": "new@example.com", "password": "a-long-passw0rd!"})
        self.assertRedirects(response, reverse("profile"))
        self.assertEqual(self.client.get(reverse("settings")).status_code, 200)

    def test_htmx_login_answers_with_redirect_header(self):
        User.objects.create_user(email="u@example.com", password="a-long-passw0rd!")
        response = self.client.post(
            reverse("login"), {"email": "u@example.com", "password": "a-long-passw0rd!"}, HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response["HX-Redirect"], reverse("profile"))

    def test_bad_login_shows_error(self):
        response = self.client.post(reverse("login"), {"email": "x@example.com", "password": "wrong"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ungültige E-Mail-Adresse oder ungültiges Passwort")
        english = self.client.post("/en" + reverse("login"), {"email": "x@example.com", "password": "wrong"})
        self.assertContains(english, "Invalid e-mail address or password")

    def test_password_change_and_profile_update(self):
        user = User.objects.create_user(email="u@example.com", password="a-long-passw0rd!", first_name="A", last_name="B")
        self.client.force_login(user)
        response = self.client.post(reverse("update_security"), {"password": "another-passw0rd!", "confirm_password": "another-passw0rd!"})
        self.assertRedirects(response, reverse("settings"))
        user.refresh_from_db()
        self.assertTrue(user.check_password("another-passw0rd!"))

        response = self.client.post(reverse("update_profile"), {"email": "u@example.com", "first_name": "Ann", "last_name": "B", "bio": "Hi"})
        self.assertRedirects(response, reverse("settings"))
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Ann")
        self.assertEqual(user.profile.bio, "Hi")

    def test_password_reset_sends_email(self):
        from django.core import mail
        User.objects.create_user(email="u@example.com", password="a-long-passw0rd!")
        self.client.post(reverse("password_reset"), {"email": "u@example.com"})
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/accounts/password/reset/", mail.outbox[0].body)

    def test_superuser_creation(self):
        admin = User.objects.create_superuser(email="root@example.com", password="a-long-passw0rd!")
        self.assertTrue(admin.is_staff and admin.is_superuser)
