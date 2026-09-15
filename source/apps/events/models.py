"""Events: launches, panels, readings and community evenings.

An event is edited like an article — the same draft / in review / scheduled /
published workflow, the same preview link — so the desk plans it on the same
board. What is different is that an event has a moment in the world as well as
a moment of publication, and the site sorts it by the first.
"""

from datetime import timedelta

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from source.apps.content.models import Media
from source.apps.content.workflow import Editorial, EditorialQuerySet
from source.apps.core.models import TimeStampedModel
from source.apps.studio.models import localized

#: How long an event runs when no end time is given. A launch or a reading is
#: still on an hour after the doors open, so it should not drop off the diary
#: the moment it starts.
DEFAULT_LENGTH = timedelta(hours=3)


class EventQuerySet(EditorialQuerySet):
    def upcoming(self, now=None):
        """Published events that have not finished yet, soonest first."""
        now = now or timezone.now()
        return self.filter(is_published=True).filter(
            models.Q(ends_at__gte=now) | models.Q(ends_at__isnull=True, starts_at__gte=now - DEFAULT_LENGTH)
        ).order_by("starts_at")

    def past(self, now=None):
        now = now or timezone.now()
        return self.filter(is_published=True).filter(
            models.Q(ends_at__lt=now) | models.Q(ends_at__isnull=True, starts_at__lt=now - DEFAULT_LENGTH)
        ).order_by("-starts_at")


class EventManager(models.Manager):
    def get_queryset(self):
        return EventQuerySet(self.model, using=self._db)

    def upcoming(self, now=None):
        return self.get_queryset().upcoming(now)

    def past(self, now=None):
        return self.get_queryset().past(now)

    def published(self):
        return self.get_queryset().filter(is_published=True)

    def due(self, now=None):
        return self.get_queryset().due(now)

    def in_status(self, status):
        return self.get_queryset().in_status(status)


class Event(Editorial, TimeStampedModel):
    KINDS = [
        ("launch", _("Edition launch")),
        ("panel", _("Panel or talk")),
        ("reading", _("Reading")),
        ("community", _("Community event")),
        ("other", _("Other")),
    ]

    title = models.CharField(max_length=255, verbose_name="Title")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Slug")
    kind = models.CharField(max_length=20, choices=KINDS, default="other", verbose_name="Kind")

    title_de = models.CharField(max_length=255, blank=True, verbose_name="Title (German)")
    title_ar = models.CharField(max_length=255, blank=True, verbose_name="Title (Arabic)")
    title_en = models.CharField(max_length=255, blank=True, verbose_name="Title (English)")
    summary_de = models.TextField(blank=True, verbose_name="Summary (German)")
    summary_ar = models.TextField(blank=True, verbose_name="Summary (Arabic)")
    summary_en = models.TextField(blank=True, verbose_name="Summary (English)")

    starts_at = models.DateTimeField(verbose_name="Starts")
    ends_at = models.DateTimeField(null=True, blank=True, verbose_name="Ends", help_text="Leave empty for an open end.")
    venue = models.CharField(max_length=160, blank=True, verbose_name="Venue")
    address = models.CharField(max_length=255, blank=True, verbose_name="Address")
    city = models.CharField(max_length=120, blank=True, verbose_name="City")
    is_online = models.BooleanField(default=False, verbose_name="Online event")

    image = models.ForeignKey(
        Media, on_delete=models.SET_NULL, null=True, blank=True, related_name="event_images", verbose_name="Picture"
    )
    registration_url = models.URLField(blank=True, verbose_name="Tickets or registration")
    is_free = models.BooleanField(default=True, verbose_name="Free entry")
    price_note = models.CharField(max_length=120, blank=True, verbose_name="Price note", help_text="e.g. 5 € at the door.")

    # Set by the workflow; see source.apps.content.workflow.
    is_published = models.BooleanField(default=False, verbose_name="Is Published")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Published At")

    objects = EventManager()

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ["-starts_at"]

    def __str__(self):
        return f"{self.title} · {self.starts_at:%d.%m.%Y}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        self.sync_publication()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("events:detail", args=[self.slug])

    @property
    def label(self):
        return localized(self, "title") or self.title

    @property
    def summary(self):
        return localized(self, "summary")

    @property
    def finishes_at(self):
        """The end time, or the assumed end for an event that gives none."""
        return self.ends_at or self.starts_at + DEFAULT_LENGTH

    @property
    def has_passed(self):
        return self.finishes_at < timezone.now()

    @property
    def is_running(self):
        """True while the doors are open, so the page can say "happening now"."""
        return self.starts_at <= timezone.now() <= self.finishes_at

    @property
    def place(self):
        """One readable line for the venue, however much of it is filled in."""
        parts = [part for part in (self.venue, self.city) if part]
        return " · ".join(parts)

    @property
    def spans_days(self):
        return bool(self.ends_at) and self.ends_at.date() != self.starts_at.date()
