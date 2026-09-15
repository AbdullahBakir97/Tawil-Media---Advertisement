"""The editorial workflow.

A piece of work moves Draft → In review → Scheduled → Published. `is_published`
stays the single answer to "is this live right now", so every existing query and
template keeps working; the status says where the piece is in the desk's process
and the schedule says when it goes live by itself.

A piece that is not live yet can still be shown to someone without an account
through its preview token, which is what an editor sends to an author or a
client for a last look.
"""

from __future__ import annotations

import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

DRAFT = "draft"
REVIEW = "review"
SCHEDULED = "scheduled"
PUBLISHED = "published"

STATUS_CHOICES = [
    (DRAFT, _("Draft")),
    (REVIEW, _("In review")),
    (SCHEDULED, _("Scheduled")),
    (PUBLISHED, _("Published")),
]

#: The order the desk works in, used for the board's columns.
BOARD_ORDER = (DRAFT, REVIEW, SCHEDULED, PUBLISHED)


class EditorialQuerySet(models.QuerySet):
    def due(self, now=None):
        """Scheduled pieces whose moment has come."""
        return self.filter(status=SCHEDULED, scheduled_for__lte=now or timezone.now())

    def in_status(self, status):
        return self.filter(status=status)


class Editorial(models.Model):
    """Status, schedule, preview token and a desk note, shared by articles and
    editions. Abstract: it adds fields, not a table."""

    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=DRAFT, db_index=True, verbose_name=_("Status"))
    scheduled_for = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Goes live"), help_text=_("Leave empty to publish by hand.")
    )
    editor_note = models.CharField(
        max_length=255, blank=True, verbose_name=_("Desk note"), help_text=_("What is still missing, for the desk only.")
    )
    preview_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        abstract = True

    def sync_publication(self):
        """Keep `is_published` and `published_at` in step with the status.

        Called from save(), so setting the status is all an editor ever has to do.
        Creating a row with `is_published=True` and no status still means "publish
        this", which is how fixtures and older code read. Once a row exists the
        status alone decides, so taking a piece down does not undo itself.
        """
        if self._state.adding and self.is_published and self.status == DRAFT:
            self.status = PUBLISHED
        live = self.status == PUBLISHED
        self.is_published = live
        if live and not self.published_at:
            self.published_at = timezone.now()
        elif not live:
            self.published_at = None

    # -- moves -------------------------------------------------------------
    def go_live(self, when=None):
        self.status = PUBLISHED
        self.published_at = when or timezone.now()
        self.save()
        return self

    def send_to_review(self, note=""):
        self.status = REVIEW
        if note:
            self.editor_note = note
        self.save()
        return self

    def unpublish(self):
        """Take the piece off the site and back to the desk."""
        return self.back_to_draft()

    def back_to_draft(self, note=""):
        self.status = DRAFT
        if note:
            self.editor_note = note
        self.save()
        return self

    def schedule(self, when):
        """Queue the piece for `when`. A moment already past goes live at once,
        which is what an editor means by "publish at 9:00" typed at 9:05."""
        if when <= timezone.now():
            return self.go_live(when)
        self.status = SCHEDULED
        self.scheduled_for = when
        self.save()
        return self

    # -- reading -----------------------------------------------------------
    @property
    def is_live(self):
        return self.status == PUBLISHED

    @property
    def is_due(self):
        return self.status == SCHEDULED and self.scheduled_for is not None and self.scheduled_for <= timezone.now()

    def preview_url(self):
        return f"{self.get_absolute_url()}?preview={self.preview_token}"

    def can_be_seen_by(self, request):
        """Live pieces are public; anything else needs a member of staff or the
        preview link."""
        if self.is_published:
            return True
        if request.user.is_authenticated and request.user.is_staff:
            return True
        return str(request.GET.get("preview", "")) == str(self.preview_token)
