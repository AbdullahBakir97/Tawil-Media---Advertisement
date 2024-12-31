from django.db import models
from source.apps.core.models import TimeStampedModel

class Advertiser(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name="Advertiser Name")
    email = models.EmailField(unique=True, verbose_name="Email Address")
    phone = models.CharField(max_length=15, blank=True, verbose_name="Phone Number")
    website = models.URLField(blank=True, verbose_name="Website")

    class Meta:
        verbose_name = "Advertiser"
        verbose_name_plural = "Advertisers"
        ordering = ["name"]

    def __str__(self):
        return self.name


class AdCampaign(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name="Campaign Name")
    advertiser = models.ForeignKey(
        Advertiser, on_delete=models.CASCADE, related_name="ad_campaigns", verbose_name="Advertiser"
    )
    budget = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Budget")
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    class Meta:
        verbose_name = "Ad Campaign"
        verbose_name_plural = "Ad Campaigns"
        ordering = ["-start_date", "name"]

    def __str__(self):
        return self.name

    def deactivate(self):
        """Deactivate the campaign."""
        self.is_active = False
        self.save()


class AdPlacement(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name="Placement Name")
    description = models.TextField(blank=True, verbose_name="Description")
    page = models.CharField(max_length=255, verbose_name="Page (e.g., homepage, article page)")
    position = models.CharField(max_length=255, verbose_name="Position (e.g., header, sidebar)")
    dimensions = models.CharField(max_length=50, verbose_name="Ad Dimensions (e.g., 300x250)")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    class Meta:
        verbose_name = "Ad Placement"
        verbose_name_plural = "Ad Placements"
        ordering = ["page", "position"]

    def __str__(self):
        return f"{self.name} ({self.page} - {self.position})"


class Advertisement(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name="Ad Name")
    campaign = models.ForeignKey(
        AdCampaign, on_delete=models.CASCADE, related_name="ads_campaign", verbose_name="Campaign"
    )
    placement = models.ForeignKey(
        AdPlacement, on_delete=models.SET_NULL, null=True, related_name="ads_placement", verbose_name="Placement"
    )
    media = models.ForeignKey(
        "content.Media", on_delete=models.SET_NULL, null=True, related_name="ads_media", verbose_name="Ad Media"
    )
    url = models.URLField(verbose_name="Target URL")
    impressions = models.PositiveIntegerField(default=0, verbose_name="Impressions")
    clicks = models.PositiveIntegerField(default=0, verbose_name="Clicks")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date")

    class Meta:
        verbose_name = "Advertisement"
        verbose_name_plural = "Advertisements"
        ordering = ["-start_date", "name"]

    def __str__(self):
        return self.name

    def increment_impressions(self):
        """Increment the number of impressions for the ad."""
        self.impressions += 1
        self.save()

    def increment_clicks(self):
        """Increment the number of clicks for the ad."""
        self.clicks += 1
        self.save()

    def deactivate(self):
        """Deactivate the ad."""
        self.is_active = False
        self.save()

    def log_performance_update(self):
        """Log the current performance metrics."""
        print(f"Ad: {self.name}, Impressions: {self.impressions}, Clicks: {self.clicks}")

    def update_performance(self, impressions, clicks):
        """Update performance metrics with new values."""
        self.impressions += impressions
        self.clicks += clicks
        self.save()


class AdPerformance(models.Model):
    advertisement = models.OneToOneField(
        Advertisement, on_delete=models.CASCADE, related_name="ads_performance", verbose_name="Advertisement"
    )
    total_impressions = models.PositiveIntegerField(default=0, verbose_name="Total Impressions")
    total_clicks = models.PositiveIntegerField(default=0, verbose_name="Total Clicks")
    click_through_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.0, verbose_name="Click-Through Rate (%)"
    )

    class Meta:
        verbose_name = "Ad Performance"
        verbose_name_plural = "Ad Performances"

    def __str__(self):
        return f"Performance for {self.advertisement.name}"

    def update_metrics(self):
        """Update click-through rate and other metrics."""
        if self.total_impressions > 0:
            self.click_through_rate = (self.total_clicks / self.total_impressions) * 100
        else:
            self.click_through_rate = 0
        self.save()

    def reset_metrics(self):
        """Reset the total impressions and clicks to zero."""
        self.total_impressions = 0
        self.total_clicks = 0
        self.click_through_rate = 0
        self.save()