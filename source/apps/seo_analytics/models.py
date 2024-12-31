from django.db import models
from source.apps.core.models import TimeStampedModel

class SEOSettings(TimeStampedModel):
    site_title = models.CharField(max_length=200, verbose_name="Site Title")
    site_description = models.TextField(verbose_name="Site Description")
    default_meta_keywords = models.TextField(verbose_name="Default Meta Keywords", blank=True)
    robots_txt = models.TextField(
        verbose_name="Robots.txt Rules", 
        default="User-agent: *\nDisallow:"
    )
    sitemap_url = models.URLField(verbose_name="Sitemap URL", blank=True)
    canonical_url = models.URLField(verbose_name="Canonical URL", blank=True)

    class Meta:
        verbose_name = "SEO Settings"
        verbose_name_plural = "SEO Settings"

    def __str__(self):
        return "Global SEO Settings"

    def update_settings(self, title=None, description=None, keywords=None):
        """Update SEO settings."""
        if title:
            self.site_title = title
        if description:
            self.site_description = description
        if keywords:
            self.default_meta_keywords = keywords
        self.save()


class SEOPageMeta(TimeStampedModel):
    url = models.URLField(unique=True, verbose_name="Page URL")
    meta_title = models.CharField(max_length=200, verbose_name="Meta Title")
    meta_description = models.TextField(verbose_name="Meta Description")
    meta_keywords = models.TextField(verbose_name="Meta Keywords", blank=True)
    canonical_url = models.URLField(verbose_name="Canonical URL", blank=True)
    no_index = models.BooleanField(default=False, verbose_name="No Index")
    no_follow = models.BooleanField(default=False, verbose_name="No Follow")

    class Meta:
        verbose_name = "SEO Page Meta"
        verbose_name_plural = "SEO Page Metadata"
        ordering = ["-created_at"]

    def __str__(self):
        return self.meta_title or self.url

    def update_meta(self, title=None, description=None, keywords=None):
        """Update meta information for the page."""
        if title:
            self.meta_title = title
        if description:
            self.meta_description = description
        if keywords:
            self.meta_keywords = keywords
        self.save()


class AnalyticsEvent(TimeStampedModel):
    event_name = models.CharField(max_length=100, verbose_name="Event Name")
    user = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="analytics_events", verbose_name="User"
    )
    url = models.URLField(verbose_name="Event URL")
    event_data = models.JSONField(verbose_name="Event Data", blank=True, null=True)
    occurred_at = models.DateTimeField(auto_now_add=True, verbose_name="Occurred At")

    class Meta:
        verbose_name = "Analytics Event"
        verbose_name_plural = "Analytics Events"
        ordering = ["-occurred_at"]

    def __str__(self):
        return f"{self.event_name} at {self.url}"

    def log_event(self):
        """Log the event data for analytics."""
        print(f"Event logged: {self.event_name} at {self.url} with data: {self.event_data}")


class PageVisit(TimeStampedModel):
    user = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="page_visits", verbose_name="User"
    )
    ip_address = models.GenericIPAddressField(verbose_name="IP Address")
    url = models.URLField(verbose_name="Visited URL")
    referrer = models.URLField(verbose_name="Referrer", blank=True, null=True)
    user_agent = models.TextField(verbose_name="User Agent", blank=True)
    visit_date = models.DateTimeField(auto_now_add=True, verbose_name="Visit Date")

    class Meta:
        verbose_name = "Page Visit"
        verbose_name_plural = "Page Visits"
        ordering = ["-visit_date"]

    def __str__(self):
        return f"Visit to {self.url} by {self.ip_address}"

    def record_visit(self):
        """Record a new page visit."""
        print(f"Recording visit: {self.url} from {self.ip_address}")


class SearchRanking(TimeStampedModel):
    keyword = models.CharField(max_length=100, verbose_name="Keyword")
    url = models.URLField(verbose_name="Page URL")
    ranking = models.PositiveIntegerField(verbose_name="Search Engine Ranking")
    search_engine = models.CharField(
        max_length=50, 
        choices=[
            ("google", "Google"),
            ("bing", "Bing"),
            ("yahoo", "Yahoo"),
        ], 
        default="google", 
        verbose_name="Search Engine"
    )
    checked_at = models.DateTimeField(auto_now_add=True, verbose_name="Checked At")

    class Meta:
        verbose_name = "Search Ranking"
        verbose_name_plural = "Search Rankings"
        ordering = ["-checked_at"]

    def __str__(self):
        return f"Keyword: {self.keyword} - Rank: {self.ranking} on {self.search_engine.capitalize()}"

    def update_ranking(self, new_ranking):
        """Update the search engine ranking for the keyword."""
        self.ranking = new_ranking
        self.save()