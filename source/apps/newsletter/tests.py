from django.test import TestCase
from django.urls import reverse

from .models import NewsletterSubscriber


class SubscribeTests(TestCase):
    def test_htmx_subscribe_creates_subscriber(self):
        response = self.client.post(reverse("newsletter:subscribe"), {"email": "A@Example.com"}, HTTP_HX_REQUEST="true")
        self.assertContains(response, "subscribed")
        self.assertTrue(NewsletterSubscriber.objects.filter(email="a@example.com").exists())

    def test_duplicate_is_reported_not_duplicated(self):
        NewsletterSubscriber.objects.create(email="a@example.com")
        response = self.client.post(reverse("newsletter:subscribe"), {"email": "a@example.com"})
        self.assertEqual(response.json()["status"], "info")
        self.assertEqual(NewsletterSubscriber.objects.count(), 1)

    def test_invalid_email(self):
        response = self.client.post(reverse("newsletter:subscribe"), {"email": "nope"})
        self.assertEqual(response.status_code, 400)
