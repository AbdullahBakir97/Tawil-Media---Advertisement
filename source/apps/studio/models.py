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

    key = models.SlugField(max_length=60, help_text=_("Where it renders, e.g. home-leaderboard, article-rectangle."), verbose_name=_("Placement key"))
    format = models.CharField(max_length=20, choices=FORMATS, default="leaderboard", verbose_name=_("Format"))
    advertiser = models.CharField(max_length=120, blank=True, verbose_name=_("Advertiser"))
    image = models.ImageField(upload_to="studio/ads/", verbose_name=_("Image"))
    url = models.URLField(blank=True, verbose_name=_("Link"))
    alt_text = models.CharField(max_length=200, blank=True, verbose_name=_("Alt text"))
    is_active = models.BooleanField(default=True, verbose_name=_("Shown on the site"))
    starts_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Runs from"))
    ends_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Runs until"))
    weight = models.PositiveSmallIntegerField(default=1, help_text=_("Higher wins when several bookings share a key."), verbose_name=_("Weight"))

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
    name = models.CharField(max_length=120, verbose_name=_("Name"))
    logo = models.ImageField(upload_to="studio/partners/", verbose_name=_("Logo"))
    url = models.URLField(blank=True, verbose_name=_("Link"))
    is_active = models.BooleanField(default=True, verbose_name=_("Shown on the site"))
    order = models.PositiveSmallIntegerField(default=0, verbose_name=_("Order"))

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class PressKit(TimeStampedModel):
    """What a journalist or a partner needs to write about us correctly.

    One row is in force at a time, the way a Theme is: `current()` returns it.
    Everything else on the press page — the logos, the colours, the facts — is
    read from the site's own data, so the kit cannot drift out of date.
    """

    name = models.CharField(max_length=120, default="Press kit", verbose_name=_("Name"))
    is_current = models.BooleanField(default=True, verbose_name=_("In force"))

    boilerplate_de = models.TextField(blank=True, verbose_name=_("Boilerplate (German)"),
                                      help_text=_("The paragraph a journalist may quote about the magazine."))
    boilerplate_ar = models.TextField(blank=True, verbose_name=_("Boilerplate (Arabic)"))
    boilerplate_en = models.TextField(blank=True, verbose_name=_("Boilerplate (English)"))

    contact_name = models.CharField(max_length=120, blank=True, verbose_name=_("Press contact"))
    contact_role_de = models.CharField(max_length=120, blank=True, verbose_name=_("Role (German)"))
    contact_role_ar = models.CharField(max_length=120, blank=True, verbose_name=_("Role (Arabic)"))
    contact_role_en = models.CharField(max_length=120, blank=True, verbose_name=_("Role (English)"))
    contact_email = models.EmailField(blank=True, verbose_name=_("Press e-mail"))
    contact_phone = models.CharField(max_length=40, blank=True, verbose_name=_("Press phone"))

    archive = models.FileField(upload_to="press/", blank=True, verbose_name=_("Everything as one download"),
                               help_text=_("Optional zip with the logos and the boilerplate."))

    class Meta:
        verbose_name = _("Press kit")
        verbose_name_plural = _("Press kits")
        ordering = ["-is_current", "-updated_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Only one kit is in force, like the default theme."""
        super().save(*args, **kwargs)
        if self.is_current:
            type(self).objects.exclude(pk=self.pk).filter(is_current=True).update(is_current=False)

    @classmethod
    def current(cls):
        return cls.objects.filter(is_current=True).first()

    @property
    def boilerplate(self):
        return localized(self, "boilerplate")

    @property
    def contact_role(self):
        return localized(self, "contact_role")


class PressAsset(TimeStampedModel):
    """A logo or a photograph a journalist may use, with the terms attached."""

    KINDS = [
        ("logo", _("Logo")),
        ("logo-mono", _("Logo, one colour")),
        ("cover", _("Cover")),
        ("portrait", _("Portrait")),
        ("photo", _("Photograph")),
    ]
    #: What the asset is laid on, so a light logo is never shown on white.
    BACKGROUNDS = [("light", _("For light backgrounds")), ("dark", _("For dark backgrounds"))]

    kit = models.ForeignKey(PressKit, on_delete=models.CASCADE, related_name="assets", verbose_name=_("Press kit"))
    label = models.CharField(max_length=120, verbose_name=_("Label"))
    kind = models.CharField(max_length=20, choices=KINDS, default="logo", verbose_name=_("Kind"))
    background = models.CharField(max_length=10, choices=BACKGROUNDS, default="light", verbose_name=_("Shown on"))
    file = models.FileField(upload_to="press/assets/", verbose_name=_("File"))
    preview = models.ImageField(upload_to="press/previews/", blank=True, verbose_name=_("Preview"),
                                help_text=_("Optional. Needed when the file itself is not a web image, e.g. an EPS."))
    credit = models.CharField(max_length=160, blank=True, verbose_name=_("Credit"))
    order = models.PositiveSmallIntegerField(default=0, verbose_name=_("Order"))

    class Meta:
        verbose_name = _("Press asset")
        verbose_name_plural = _("Press assets")
        ordering = ["order", "label"]

    def __str__(self):
        return self.label

    @property
    def thumbnail(self):
        """What to show on the page: the preview if there is one, else the file
        itself when a browser can draw it."""
        if self.preview:
            return self.preview
        return self.file if self.file.name.lower().endswith((".png", ".jpg", ".jpeg", ".svg", ".webp")) else None

    @property
    def extension(self):
        return self.file.name.rsplit(".", 1)[-1].upper() if "." in self.file.name else ""


class Testimonial(TimeStampedModel):
    quote_de = models.TextField(verbose_name=_("Quote (German)"))
    quote_ar = models.TextField(blank=True, verbose_name=_("Quote (Arabic)"))
    quote_en = models.TextField(blank=True, verbose_name=_("Quote (English)"))
    name = models.CharField(max_length=120, verbose_name=_("Name"))
    role = models.CharField(max_length=160, blank=True, help_text=_("Role and company"), verbose_name=_("Role"))
    avatar = models.ImageField(upload_to="studio/testimonials/", blank=True, verbose_name=_("Portrait"))
    is_active = models.BooleanField(default=True, verbose_name=_("Shown on the site"))
    order = models.PositiveSmallIntegerField(default=0, verbose_name=_("Order"))

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

    page = models.CharField(max_length=20, choices=PAGES, default="help", verbose_name=_("Page"))
    question_de = models.CharField(max_length=200, verbose_name=_("Question (German)"))
    question_ar = models.CharField(max_length=200, blank=True, verbose_name=_("Question (Arabic)"))
    question_en = models.CharField(max_length=200, blank=True, verbose_name=_("Question (English)"))
    answer_de = models.TextField(verbose_name=_("Answer (German)"))
    answer_ar = models.TextField(blank=True, verbose_name=_("Answer (Arabic)"))
    answer_en = models.TextField(blank=True, verbose_name=_("Answer (English)"))
    is_active = models.BooleanField(default=True, verbose_name=_("Shown on the site"))
    order = models.PositiveSmallIntegerField(default=0, verbose_name=_("Order"))

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
    year = models.PositiveSmallIntegerField(verbose_name=_("Year"))
    title_de = models.CharField(max_length=120, verbose_name=_("Title (German)"))
    title_ar = models.CharField(max_length=120, blank=True, verbose_name=_("Title (Arabic)"))
    title_en = models.CharField(max_length=120, blank=True, verbose_name=_("Title (English)"))
    text_de = models.TextField(blank=True, verbose_name=_("Text (German)"))
    text_ar = models.TextField(blank=True, verbose_name=_("Text (Arabic)"))
    text_en = models.TextField(blank=True, verbose_name=_("Text (English)"))
    is_active = models.BooleanField(default=True, verbose_name=_("Shown on the site"))

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
