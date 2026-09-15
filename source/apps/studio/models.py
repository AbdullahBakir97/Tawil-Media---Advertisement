"""Studio: everything editors change from inside the site.

Themes give an edition, a page or the whole site its own look. HeroConfig holds
the home hero design and copy. Announcements feed the line above the navbar,
AdSlots the booked placements. Partners, testimonials, FAQ entries and milestones
are the trust blocks used on the company pages. MagazinePage stores the rendered
pages of an edition's PDF for the flip-book reader.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from source.apps.core.models import TimeStampedModel

LANGS = [code for code, _name in settings.LANGUAGES]


def localized(obj, field):
    """Return ``obj.<field>_<lang>`` for the active language, falling back to the default."""
    lang = (get_language() or settings.LANGUAGE_CODE).split("-")[0]
    for code in (lang, settings.LANGUAGE_CODE.split("-")[0], *LANGS):
        value = getattr(obj, f"{field}_{code}", "")
        if value:
            return value
    return ""


class Theme(TimeStampedModel):
    """A named set of design tokens. Assign to an edition, a page or the site."""

    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=80, unique=True)
    accent = models.CharField(max_length=7, default="#f2b25c", help_text=_("Highlight colour, e.g. gold."))
    brand = models.CharField(max_length=7, default="#062a4a", help_text=_("Brand surface colour, e.g. navy."))
    brand_deep = models.CharField(max_length=7, default="#031428")
    interaction = models.CharField(max_length=7, default="#0284c7", help_text=_("Links and buttons."))
    display_font = models.CharField(
        max_length=20,
        choices=[("playfair", "Playfair Display"), ("system-serif", "System serif"), ("system-sans", "System sans")],
        default="playfair",
    )
    radius = models.PositiveSmallIntegerField(default=20, help_text=_("Corner radius in px for cards and panels."))
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def css_vars(self):
        font = {
            "playfair": '"Playfair Display", "Amiri", Georgia, serif',
            "system-serif": 'Georgia, "Times New Roman", serif',
            "system-sans": '"Source Sans 3", system-ui, sans-serif',
        }[self.display_font]
        return (
            f"--gold-400:{self.accent};--accent:{self.accent};--bg-brand:{self.brand};--navy-800:{self.brand};"
            f"--bg-brand-deep:{self.brand_deep};--navy-900:{self.brand_deep};--color-primary:{self.interaction};"
            f"--sky-600:{self.interaction};--font-display:{font};--radius-2xl:{self.radius}px;"
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_default:
            Theme.objects.exclude(pk=self.pk).update(is_default=False)


class HeroConfig(TimeStampedModel):
    """The home hero: which design, what it says, what it shows. One row per placement."""

    VARIANTS = [
        ("front", _("Front page · masthead, glass text, book stack, ticker")),
        ("light", _("Light editorial · cream broadsheet, dark type")),
        ("immersive", _("Immersive · full-bleed photo, floating story cards")),
        ("newsroom", _("Newsroom · lead image, columns, edition sidebar")),
        ("classic", _("Classic · logos, director, edition slider")),
    ]

    placement = models.SlugField(max_length=40, unique=True, default="home")
    variant = models.CharField(max_length=20, choices=VARIANTS, default="front")
    theme = models.ForeignKey(Theme, null=True, blank=True, on_delete=models.SET_NULL)
    background = models.ImageField(upload_to="studio/hero/", blank=True)
    show_masthead = models.BooleanField(default=True)
    show_stats = models.BooleanField(default=True)
    show_ticker = models.BooleanField(default=True)
    show_partners = models.BooleanField(default=False)
    show_issue_facts = models.BooleanField(default=True)

    kicker_de = models.CharField(max_length=120, blank=True)
    kicker_ar = models.CharField(max_length=120, blank=True)
    kicker_en = models.CharField(max_length=120, blank=True)
    headline_de = models.CharField(max_length=200, blank=True, help_text=_("Wrap a word in *asterisks* to colour it."))
    headline_ar = models.CharField(max_length=200, blank=True)
    headline_en = models.CharField(max_length=200, blank=True)
    dek_de = models.TextField(blank=True)
    dek_ar = models.TextField(blank=True)
    dek_en = models.TextField(blank=True)
    primary_label_de = models.CharField(max_length=60, blank=True)
    primary_label_ar = models.CharField(max_length=60, blank=True)
    primary_label_en = models.CharField(max_length=60, blank=True)
    primary_url = models.CharField(max_length=200, blank=True, help_text=_("Leave empty to link the latest edition."))
    secondary_label_de = models.CharField(max_length=60, blank=True)
    secondary_label_ar = models.CharField(max_length=60, blank=True)
    secondary_label_en = models.CharField(max_length=60, blank=True)
    secondary_url = models.CharField(max_length=200, blank=True, help_text=_("Leave empty to link the advertising page."))

    pages_label = models.CharField(max_length=40, blank=True, help_text=_("e.g. 96 pages"))
    price_label = models.CharField(max_length=40, blank=True, help_text=_("e.g. 4,90 € · free online"))

    class Meta:
        verbose_name = _("Hero")
        verbose_name_plural = _("Heroes")

    def __str__(self):
        return f"{self.placement} · {self.get_variant_display()}"

    # Localised accessors used by the templates
    @property
    def kicker(self):
        return localized(self, "kicker")

    @property
    def headline(self):
        return localized(self, "headline")

    @property
    def dek(self):
        return localized(self, "dek")

    @property
    def primary_label(self):
        return localized(self, "primary_label")

    @property
    def secondary_label(self):
        return localized(self, "secondary_label")

    @classmethod
    def for_placement(cls, placement="home"):
        obj, _created = cls.objects.get_or_create(placement=placement)
        return obj


class Announcement(TimeStampedModel):
    """One item on the line above the navbar."""

    KINDS = [("editorial", _("Editorial")), ("ad", _("Advertising")), ("live", _("Live"))]

    kind = models.CharField(max_length=12, choices=KINDS, default="editorial")
    text_de = models.CharField(max_length=160)
    text_ar = models.CharField(max_length=160, blank=True)
    text_en = models.CharField(max_length=160, blank=True)
    url = models.CharField(max_length=300, blank=True)
    is_active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.text_de

    @property
    def text(self):
        return localized(self, "text")

    @classmethod
    def live(cls):
        now = timezone.now()
        return (
            cls.objects.filter(is_active=True)
            .filter(models.Q(starts_at__isnull=True) | models.Q(starts_at__lte=now))
            .filter(models.Q(ends_at__isnull=True) | models.Q(ends_at__gte=now))
        )


class AdSlot(TimeStampedModel):
    """A booked placement, rendered with ``{% ad_slot "key" %}``."""

    FORMATS = [
        ("leaderboard", "Leaderboard · 728×90"),
        ("billboard", "Billboard · 970×250"),
        ("rectangle", "Rectangle · 300×250"),
        ("skyscraper", "Skyscraper · 300×600"),
        ("mobile", "Mobile banner · 320×100"),
    ]

    key = models.SlugField(max_length=60, help_text=_("Where it renders, e.g. home-leaderboard, article-rectangle."))
    format = models.CharField(max_length=20, choices=FORMATS, default="leaderboard")
    advertiser = models.CharField(max_length=120, blank=True)
    image = models.ImageField(upload_to="studio/ads/")
    url = models.URLField(blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    weight = models.PositiveSmallIntegerField(default=1, help_text=_("Higher wins when several bookings share a key."))

    class Meta:
        ordering = ["key", "-weight"]

    def __str__(self):
        return f"{self.key} · {self.advertiser or self.get_format_display()}"

    @classmethod
    def current(cls, key):
        now = timezone.now()
        return (
            cls.objects.filter(key=key, is_active=True)
            .filter(models.Q(starts_at__isnull=True) | models.Q(starts_at__lte=now))
            .filter(models.Q(ends_at__isnull=True) | models.Q(ends_at__gte=now))
            .first()
        )


class Partner(TimeStampedModel):
    name = models.CharField(max_length=120)
    logo = models.ImageField(upload_to="studio/partners/")
    url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Testimonial(TimeStampedModel):
    quote_de = models.TextField()
    quote_ar = models.TextField(blank=True)
    quote_en = models.TextField(blank=True)
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=160, blank=True, help_text=_("Role and company"))
    avatar = models.ImageField(upload_to="studio/testimonials/", blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.name

    @property
    def quote(self):
        return localized(self, "quote")

    @property
    def initials(self):
        return "".join(part[0] for part in self.name.split()[:2]).upper()


class FAQ(TimeStampedModel):
    PAGES = [("help", _("Help")), ("advertise", _("Advertising")), ("about", _("About"))]

    page = models.CharField(max_length=20, choices=PAGES, default="help")
    question_de = models.CharField(max_length=200)
    question_ar = models.CharField(max_length=200, blank=True)
    question_en = models.CharField(max_length=200, blank=True)
    answer_de = models.TextField()
    answer_ar = models.TextField(blank=True)
    answer_en = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["page", "order"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"

    def __str__(self):
        return self.question_de

    @property
    def question(self):
        return localized(self, "question")

    @property
    def answer(self):
        return localized(self, "answer")


class Milestone(TimeStampedModel):
    year = models.PositiveSmallIntegerField()
    title_de = models.CharField(max_length=120)
    title_ar = models.CharField(max_length=120, blank=True)
    title_en = models.CharField(max_length=120, blank=True)
    text_de = models.TextField(blank=True)
    text_ar = models.TextField(blank=True)
    text_en = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["year"]

    def __str__(self):
        return f"{self.year} · {self.title_de}"

    @property
    def title(self):
        return localized(self, "title")

    @property
    def text(self):
        return localized(self, "text")


class MagazinePage(models.Model):
    """One rendered page of an edition's PDF, for the flip-book reader."""

    magazine = models.ForeignKey("content.Magazine", on_delete=models.CASCADE, related_name="pages")
    number = models.PositiveIntegerField()
    image = models.ImageField(upload_to="magazines/pages/")
    thumbnail = models.ImageField(upload_to="magazines/thumbs/", blank=True)
    width = models.PositiveIntegerField(default=0)
    height = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["magazine", "number"]
        unique_together = [("magazine", "number")]

    def __str__(self):
        return f"{self.magazine} · p.{self.number}"
