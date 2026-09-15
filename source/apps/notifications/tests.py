from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Notification


class NotificationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email="u@example.com", password="a-long-passw0rd!")
        self.client.force_login(self.user)
        self.note = Notification.notify(self.user, "Hello", "World")

    def test_badge_count_in_context(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.context["unread_notifications_count"], 1)

    def test_dropdown_and_list(self):
        self.assertContains(self.client.get(reverse("notifications:notifications_dropdown")), "Hello")
        self.assertContains(self.client.get(reverse("notifications:list")), "Hello")

    def test_mark_read(self):
        response = self.client.post(reverse("notifications:mark_read", args=[self.note.id]))
        self.assertEqual(response.json()["status"], "success")
        self.note.refresh_from_db()
        self.assertTrue(self.note.read)
        self.assertEqual(self.client.get(reverse("notifications:unread_count")).json()["unread_count"], 0)

    def test_other_users_notifications_are_hidden(self):
        other = get_user_model().objects.create_user(email="o@example.com", password="a-long-passw0rd!")
        secret = Notification.notify(other, "Secret", "x")
        self.assertEqual(self.client.post(reverse("notifications:mark_read", args=[secret.id])).status_code, 404)
        self.assertNotContains(self.client.get(reverse("notifications:list")), "Secret")
