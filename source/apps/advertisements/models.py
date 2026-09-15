import logging

from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _

from source.apps.core.models import TimeStampedModel

logger = logging.getLogger(__name__)


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
        AdPlacement, on_delete=models.SET_NULL, null=True, blank=True, related_name="ads_placement", verbose_name="Placement"
    )
    media = models.ForeignKey(
        "content.Media", on_delete=models.SET_NULL, null=True, blank=True, related_name="ads_media", verbose_name="Ad Media"
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
        """Atomically increment the number of impressions for the ad."""
        Advertisement.objects.filter(pk=self.pk).update(impressions=F("impressions") + 1)
        self.refresh_from_db(fields=["impressions"])

    def increment_clicks(self):
        """Atomically increment the number of clicks for the ad."""
        Advertisement.objects.filter(pk=self.pk).update(clicks=F("clicks") + 1)
        self.refresh_from_db(fields=["clicks"])

    def deactivate(self):
        """Deactivate the ad."""
        self.is_active = False
        self.save()

    def log_performance_update(self):
        """Log the current performance metrics."""
        logger.info("Ad %s: impressions=%s clicks=%s", self.name, self.impressions, self.clicks)

    def update_performance(self, impressions, clicks):
        """Update performance metrics with new values."""
        Advertisement.objects.filter(pk=self.pk).update(
            impressions=F("impressions") + impressions, clicks=F("clicks") + clicks
        )
        self.refresh_from_db(fields=["impressions", "clicks"])


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


# ---------------------------------------------------------------------------
# What we sell: the rate card, the media kit and the requests that come back.
# ---------------------------------------------------------------------------


class RateCard(TimeStampedModel):
    """One sellable placement: a print page, a web banner, a newsletter slot."""

    CHANNELS = [
        ("print", _("Print")),
        ("digital", _("Digital")),
        ("social", _("Social")),
        ("bundle", _("Bundle")),
    ]
    UNITS = [
        ("edition", _("per edition")),
        ("week", _("per week")),
        ("month", _("per month")),
        ("send", _("per send")),
        ("package", _("per package")),
    ]

    channel = models.CharField(max_length=12, choices=CHANNELS, default="print", verbose_name=_("Channel"))
    slug = models.SlugField(max_length=80, unique=True, verbose_name=_("Slug"))
    name_de = models.CharField(max_length=120, verbose_name=_("Name (German)"))
    name_ar = models.CharField(max_length=120, blank=True, verbose_name=_("Name (Arabic)"))
    name_en = models.CharField(max_length=120, blank=True, verbose_name=_("Name (English)"))
    description_de = models.TextField(blank=True, verbose_name=_("Description (German)"))
    description_ar = models.TextField(blank=True, verbose_name=_("Description (Arabic)"))
    description_en = models.TextField(blank=True, verbose_name=_("Description (English)"))

    specs = models.CharField(max_length=160, blank=True, verbose_name=_("Specification"), help_text="e.g. 210 × 297 mm + 3 mm bleed, CMYK")
    width = models.PositiveIntegerField(null=True, blank=True, help_text="Width in mm (print) or px (digital), for the size preview.", verbose_name=_("Width"))
    height = models.PositiveIntegerField(null=True, blank=True, help_text="Height in mm (print) or px (digital).", verbose_name=_("Height"))

    price = models.DecimalField(max_digits=9, decimal_places=2, default=0, verbose_name=_("Price"))
    unit = models.CharField(max_length=12, choices=UNITS, default="edition", verbose_name=_("Billed"))
    is_featured = models.BooleanField(default=False, verbose_name=_("Highlight on the rate card"))
    is_active = models.BooleanField(default=True, verbose_name=_("Shown on the site"))
    order = models.PositiveSmallIntegerField(default=0, verbose_name=_("Order"))

    class Meta:
        verbose_name = "Rate card entry"
        verbose_name_plural = "Rate card"
        ordering = ["channel", "order", "price"]

    def __str__(self):
        return f"{self.get_channel_display()} · {self.name_de}"

    @property
    def name(self):
        from source.apps.studio.models import localized

        return localized(self, "name")

    @property
    def description(self):
        from source.apps.studio.models import localized

        return localized(self, "description")

    @property
    def aspect_ratio(self):
        """CSS aspect-ratio for the size preview, or None when the size is unknown."""
        if self.width and self.height:
            return f"{self.width} / {self.height}"
        return None

    @property
    def size_label(self):
        if not (self.width and self.height):
            return ""
        unit = "mm" if self.channel == "print" else "px"
        return f"{self.width} × {self.height} {unit}"


class MediaKit(TimeStampedModel):
    """The downloadable media kit. The newest active one is offered."""

    title = models.CharField(max_length=120, default="Media kit", verbose_name=_("Title"))
    file = models.FileField(upload_to="advertising/media-kit/", verbose_name=_("File"))
    year = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_("Year"))
    is_active = models.BooleanField(default=True, verbose_name=_("Shown on the site"))

    class Meta:
        verbose_name = "Media kit"
        verbose_name_plural = "Media kits"
        ordering = ["-year", "-created_at"]

    def __str__(self):
        return f"{self.title} {self.year or ''}".strip()

    @classmethod
    def current(cls):
        return cls.objects.filter(is_active=True).first()


class CampaignRequest(TimeStampedModel):
    """A planned campaign sent from the advertising page. Never charged automatically."""

    STATUS = [
        ("new", _("New")),
        ("contacted", _("Contacted")),
        ("quoted", _("Quoted")),
        ("won", _("Won")),
        ("lost", _("Lost")),
    ]

    company = models.CharField(max_length=160, verbose_name="Company")
    contact_name = models.CharField(max_length=160, verbose_name="Contact")
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    message = models.TextField(blank=True)
    editions = models.ManyToManyField("content.Magazine", blank=True, related_name="campaign_requests")
    estimate = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Estimate shown")
    status = models.CharField(max_length=12, choices=STATUS, default="new")
    language = models.CharField(max_length=5, blank=True)

    class Meta:
        verbose_name = "Campaign request"
        verbose_name_plural = "Campaign requests"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.company} · {self.created_at:%Y-%m-%d}"

    @property
    def total(self):
        return sum(item.line_total for item in self.items.all())

    def summary_lines(self):
        return [f"{item.quantity} × {item.rate_card.name_de} ({item.line_total} €)" for item in self.items.all()]


class CampaignRequestItem(models.Model):
    request = models.ForeignKey(CampaignRequest, on_delete=models.CASCADE, related_name="items")
    rate_card = models.ForeignKey(RateCard, on_delete=models.PROTECT, related_name="request_items")
    quantity = models.PositiveSmallIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Requested placement"
        verbose_name_plural = "Requested placements"

    def __str__(self):
        return f"{self.quantity} × {self.rate_card}"

    @property
    def line_total(self):
        return self.quantity * self.unit_price
