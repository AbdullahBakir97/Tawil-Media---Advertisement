"""Render flip-book pages whenever an edition gets a new PDF."""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from source.apps.content.models import Magazine

from .services import render_magazine_pages

log = logging.getLogger(__name__)


@receiver(post_save, sender=Magazine)
def render_pages_on_pdf_change(sender, instance, **kwargs):
    if not instance.pdf:
        return
    if instance.pdf_rendered == instance.pdf.name and instance.pages.exists():
        return
    try:
        render_magazine_pages(instance)
    except Exception:  # pragma: no cover - never break a save because rendering failed
        log.exception("Could not render pages for %s", instance)
