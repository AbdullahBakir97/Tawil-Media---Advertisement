"""The newsletter: who receives it, and what an issue is made of.

An issue is assembled from blocks that point at things the site already has —
an article, the current edition, an event, a booked ad slot — so the letter
stays correct as those change and nothing is copied by hand. The desk writes
only the subject, the preheader and a short intro.
"""

import uuid

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

LANGUAGES = [("de", _("German")), ("ar", _("Arabic")), ("en", _("English"))]


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    language = models.CharField(max_length=5, choices=LANGUAGES, default="de", verbose_name=_("Language"))
    is_active = models.BooleanField(default=True)
    #: In the unsubscribe link of every letter. Unguessable, so no one can
    #: unsubscribe somebody else.
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Newsletter Subscriber"
        verbose_name_plural = "Newsletter Subscribers"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email

    def unsubscribe_url(self):
        return reverse("newsletter:unsubscribe", args=[self.token])


class Issue(models.Model):
    """One letter. It goes to the subscribers who read that language."""

    DRAFT, SCHEDULED, SENT = "draft", "scheduled", "sent"
    STATUS = [(DRAFT, _("Draft")), (SCHEDULED, _("Scheduled")), (SENT, _("Sent"))]

    language = models.CharField(max_length=5, choices=LANGUAGES, default="de", verbose_name=_("Language"))
    subject = models.CharField(max_length=180, verbose_name=_("Subject"))
    preheader = models.CharField(
        max_length=180, blank=True, verbose_name=_("Preheader"),
        help_text=_("The line shown after the subject in the inbox."),
    )
    intro = models.TextField(blank=True, verbose_name=_("Intro"), help_text=_("A few lines from the desk."))

    status = models.CharField(max_length=12, choices=STATUS, default=DRAFT, db_index=True, verbose_name=_("Status"))
    scheduled_for = models.DateTimeField(null=True, blank=True, verbose_name=_("Goes out"))
    sent_at = models.DateTimeField(null=True, blank=True, editable=False, verbose_name=_("Sent"))
    sent_count = models.PositiveIntegerField(default=0, editable=False, verbose_name=_("Recipients"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Newsletter issue")
        verbose_name_plural = _("Newsletter issues")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} ({self.get_language_display()})"

    @property
    def is_sent(self):
        return self.status == self.SENT

    @property
    def is_due(self):
        return self.status == self.SCHEDULED and self.scheduled_for is not None and self.scheduled_for <= timezone.now()

    def recipients(self):
        """Active subscribers who read this issue's language."""
        return NewsletterSubscriber.objects.filter(is_active=True, language=self.language)


class IssueBlock(models.Model):
    """One piece of an issue, pointing at something the site already holds."""

    ARTICLE, LEAD, EDITION, EVENT, AD, TEXT = "article", "lead", "edition", "event", "ad", "text"
    KINDS = [
        (LEAD, _("Lead story")),
        (ARTICLE, _("Article")),
        (EDITION, _("Edition")),
        (EVENT, _("Event")),
        (AD, _("Advertisement")),
        (TEXT, _("Text")),
    ]

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="blocks")
    kind = models.CharField(max_length=12, choices=KINDS, default=ARTICLE, verbose_name=_("Kind"))
    order = models.PositiveSmallIntegerField(default=0, verbose_name=_("Order"))

    article = models.ForeignKey("content.Article", on_delete=models.CASCADE, null=True, blank=True)
    edition = models.ForeignKey("content.Magazine", on_delete=models.CASCADE, null=True, blank=True)
    event = models.ForeignKey("events.Event", on_delete=models.CASCADE, null=True, blank=True)
    ad_slot = models.ForeignKey("studio.AdSlot", on_delete=models.CASCADE, null=True, blank=True)

    heading = models.CharField(max_length=180, blank=True, verbose_name=_("Heading"),
                               help_text=_("Leave empty to use the piece's own title."))
    body = models.TextField(blank=True, verbose_name=_("Text"))

    class Meta:
        verbose_name = _("Block")
        verbose_name_plural = _("Blocks")
        ordering = ["order", "pk"]

    def __str__(self):
        return f"{self.get_kind_display()}: {self.title or '—'}"

    @property
    def target(self):
        """Whatever this block points at, or None for a text block."""
        return self.article or self.edition or self.event

    @property
    def is_empty(self):
        """A block that points at nothing and says nothing renders nothing."""
        if self.kind == self.TEXT:
            return not (self.heading or self.body)
        if self.kind == self.AD:
            return self.ad_slot is None
        return self.target is None

    @property
    def title(self):
        if self.heading:
            return self.heading
        if self.kind == self.AD and self.ad_slot_id:
            return self.ad_slot.alt_text or self.ad_slot.advertiser or self.ad_slot.key
        target = self.target
        if target is None:
            return ""
        return getattr(target, "label", None) or target.title

    @property
    def text(self):
        if self.body:
            return self.body
        target = self.target
        if target is None:
            return ""
        return getattr(target, "summary", "") or getattr(target, "excerpt", "") or ""
