import re
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from source.apps.content.models import Article
from source.apps.seo_analytics import reporting
from source.apps.seo_analytics.middleware import anonymise
from source.apps.seo_analytics.models import PageVisit

READER = "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Safari/537.36"


def a_visit(url="/articles/eine-geschichte/", days_ago=0, ip="203.0.113.7", referrer=None):
    visit = PageVisit.objects.create(url=url, ip_address=ip, referrer=referrer, user_agent=READER)
    # visit_date is auto_now_add, so move it afterwards to place it in the past.
    moment = timezone.now() - timedelta(days=days_ago)
    PageVisit.objects.filter(pk=visit.pk).update(visit_date=moment)
    visit.refresh_from_db()
    return visit


class AnonymisingTests(TestCase):
    def test_an_ipv4_address_keeps_only_its_network(self):
        self.assertEqual(anonymise("203.0.113.42"), "203.0.113.0")

    def test_an_ipv6_address_keeps_only_its_prefix(self):
        self.assertEqual(anonymise("2001:db8:1234:5678::1"), "2001:db8:1234::")

    def test_an_unreadable_address_does_not_raise(self):
        self.assertEqual(anonymise("not-an-address"), "0.0.0.0")


class RecordingTests(TestCase):
    def test_a_page_a_reader_opens_is_recorded_once(self):
        self.client.get("/", HTTP_USER_AGENT=READER)
        self.assertEqual(PageVisit.objects.count(), 1)

    def test_the_stored_address_is_already_truncated(self):
        self.client.get("/", HTTP_USER_AGENT=READER, REMOTE_ADDR="203.0.113.42")
        self.assertEqual(PageVisit.objects.get().ip_address, "203.0.113.0")

    def test_crawlers_are_not_counted_as_readers(self):
        self.client.get("/", HTTP_USER_AGENT="Googlebot/2.1 (+http://www.google.com/bot.html)")
        self.assertEqual(PageVisit.objects.count(), 0)

    def test_a_request_without_a_user_agent_is_not_counted(self):
        self.client.get("/")
        self.assertEqual(PageVisit.objects.count(), 0)

    def test_do_not_track_is_honoured(self):
        self.client.get("/", HTTP_USER_AGENT=READER, HTTP_DNT="1")
        self.assertEqual(PageVisit.objects.count(), 0)

    def test_the_desk_browsing_its_own_site_is_not_readership(self):
        staff = get_user_model().objects.create_user(email="desk@example.com", password="pw-for-tests", is_staff=True)
        self.client.force_login(staff)
        self.client.get("/", HTTP_USER_AGENT=READER)
        self.assertEqual(PageVisit.objects.count(), 0)

    def test_the_studio_and_the_admin_are_never_recorded(self):
        staff = get_user_model().objects.create_user(email="desk2@example.com", password="pw-for-tests", is_staff=True)
        self.client.force_login(staff)
        self.client.get("/studio/", HTTP_USER_AGENT=READER)
        self.client.logout()
        self.client.get("/admin/", HTTP_USER_AGENT=READER)
        self.assertEqual(PageVisit.objects.count(), 0)

    def test_a_missing_page_is_not_counted(self):
        self.client.get("/kein-solcher-pfad/", HTTP_USER_AGENT=READER)
        self.assertEqual(PageVisit.objects.count(), 0)

    @override_settings(ANALYTICS_ENABLED=False)
    def test_recording_can_be_switched_off(self):
        self.client.get("/", HTTP_USER_AGENT=READER)
        self.assertEqual(PageVisit.objects.count(), 0)


class ReportingTests(TestCase):
    def test_the_series_covers_every_day_including_the_quiet_ones(self):
        a_visit(days_ago=0)
        a_visit(days_ago=3)
        series = reporting.daily_series(7)
        self.assertEqual(len(series), 7)
        self.assertEqual(sum(day["visits"] for day in series), 2)
        self.assertEqual([day["visits"] for day in series].count(0), 5)

    def test_visits_outside_the_window_are_left_out(self):
        a_visit(days_ago=1)
        a_visit(days_ago=40)
        self.assertEqual(reporting.totals(7)["visits"], 1)
        self.assertEqual(reporting.totals(90)["visits"], 2)

    def test_networks_are_counted_rather_than_page_views(self):
        a_visit(ip="203.0.113.0")
        a_visit(ip="203.0.113.0")
        a_visit(ip="198.51.100.0")
        totals = reporting.totals(7)
        self.assertEqual(totals["visits"], 3)
        self.assertEqual(totals["networks"], 2)

    def test_the_most_read_pages_carry_the_headline_when_there_is_one(self):
        article = Article.objects.create(title="Die Stadt am Morgen", content="x", slug="die-stadt-am-morgen")
        article.go_live()
        for _ in range(3):
            a_visit(url="/articles/die-stadt-am-morgen/")
        a_visit(url="/impressum/")
        pages = reporting.top_pages(7)
        self.assertEqual(pages[0]["label"], "Die Stadt am Morgen")
        self.assertEqual(pages[0]["visits"], 3)
        self.assertEqual(pages[1]["label"], "/impressum/")

    def test_referrers_are_grouped_by_site(self):
        a_visit(referrer="https://www.example.com/a")
        a_visit(referrer="https://example.com/b")
        a_visit(referrer="https://anderer.de/c")
        referrers = reporting.top_referrers(7)
        self.assertEqual(referrers[0], {"label": "example.com", "visits": 2})
        self.assertEqual(referrers[1]["label"], "anderer.de")

    def test_the_chart_geometry_fits_inside_its_box(self):
        for day in range(5):
            a_visit(days_ago=day)
        chart = reporting.chart_geometry(reporting.daily_series(5), width=100, height=50, pad=4)
        self.assertEqual(len(chart["dots"]), 5)
        for dot in chart["dots"]:
            self.assertGreaterEqual(dot["x"], 4)
            self.assertLessEqual(dot["x"], 96)
            self.assertGreaterEqual(dot["y"], 4)
            self.assertLessEqual(dot["y"], 46)

    def test_an_empty_window_still_produces_a_drawable_chart(self):
        chart = reporting.chart_geometry(reporting.daily_series(7))
        self.assertEqual(chart["peak"], 1)
        self.assertEqual(len(chart["dots"]), 7)


class AnalyticsPanelTests(TestCase):
    def setUp(self):
        self.client.force_login(
            get_user_model().objects.create_user(email="desk@example.com", password="pw-for-tests", is_staff=True)
        )

    def test_the_panel_is_staff_only(self):
        self.client.logout()
        self.assertEqual(self.client.get("/studio/analytics/").status_code, 302)

    def test_it_opens_with_nothing_recorded(self):
        response = self.client.get("/studio/analytics/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "empty-state")

    def test_it_shows_the_totals_and_the_most_read_page(self):
        article = Article.objects.create(title="Die Stadt am Morgen", content="x", slug="die-stadt-am-morgen")
        article.go_live()
        for _ in range(4):
            a_visit(url="/articles/die-stadt-am-morgen/")
        response = self.client.get("/studio/analytics/")
        self.assertContains(response, "Die Stadt am Morgen")
        self.assertEqual(response.context["totals"]["visits"], 4)

    def test_the_period_can_be_changed(self):
        a_visit(days_ago=20)
        self.assertEqual(self.client.get("/studio/analytics/?days=7").context["totals"]["visits"], 0)
        self.assertEqual(self.client.get("/studio/analytics/?days=30").context["totals"]["visits"], 1)

    def test_a_nonsense_period_falls_back_to_the_default(self):
        for value in ("abc", "999", ""):
            with self.subTest(value=value):
                self.assertEqual(self.client.get(f"/studio/analytics/?days={value}").context["days"], 30)

    def test_the_chart_coordinates_survive_a_comma_decimal_locale(self):
        """German formats 470.48 as "470,48", which SVG will not accept — the
        chart has to opt out of locale formatting for its geometry."""
        for _ in range(3):
            a_visit()
        html = self.client.get("/studio/analytics/").content.decode()
        coordinates = re.findall(r'c[xy]="([^"]+)"', html)
        self.assertTrue(coordinates)
        for value in coordinates:
            with self.subTest(value=value):
                float(value)  # raises if a comma slipped in

    def test_the_numbers_are_available_as_a_table_as_well_as_a_chart(self):
        a_visit()
        self.assertContains(self.client.get("/studio/analytics/"), "chart-table")
