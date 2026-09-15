"""Turning an issue into an e-mail.

Each block is flattened into plain values — a title, a line of text, one
absolute URL, one absolute image URL — before the template sees it, because a
mail client has no session, no relative paths and no template tags. Everything
is resolved here, once, so the template stays a layout and nothing else.
"""

from __future__ import annotations

from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import translation
from django.utils.html import strip_tags
from django.utils.text import Truncator

from .models import IssueBlock


def site_url() -> str:
    """The public origin, for links that must work from an inbox."""
    base = (getattr(settings, "SITE_URL", "") or "").rstrip("/")
    if base:
        return base
    host = next(iter(getattr(settings, "ALLOWED_HOSTS", []) or ["localhost:8000"]))
    host = "localhost:8000" if host in ("*", "") else host
    scheme = "http" if host.startswith(("localhost", "127.")) else "https"
    return f"{scheme}://{host}"


def _absolute(path: str) -> str:
    if not path:
        return ""
    return path if path.startswith(("http://", "https://")) else f"{site_url()}{path}"


def _image_for(block) -> str:
    """The picture a block should show, as an absolute URL."""
    if block.kind == IssueBlock.AD and block.ad_slot_id:
        return _absolute(block.ad_slot.image.url) if block.ad_slot.image else ""

    target = block.target
    if target is None:
        return ""
    for attribute in ("cover", "cover_image", "image"):
        media = getattr(target, attribute, None)
        if media and getattr(media, "file", None):
            return _absolute(media.file.url)
    return ""


def _url_for(block) -> str:
    if block.kind == IssueBlock.AD and block.ad_slot_id:
        return block.ad_slot.url or site_url()
    target = block.target
    if target is None or not hasattr(target, "get_absolute_url"):
        return site_url()
    return _absolute(target.get_absolute_url())


def _meta_for(block) -> str:
    """A second line: the date of an event, the issue number of an edition."""
    if block.kind == IssueBlock.EVENT and block.event_id:
        event = block.event
        place = f" · {event.place}" if event.place else ""
        return f"{event.starts_at:%d.%m.%Y, %H:%M}{place}"
    if block.kind == IssueBlock.EDITION and block.edition_id and block.edition.issue_number:
        return f"№ {block.edition.issue_number}"
    return ""


def flatten(block) -> dict:
    """One block as the plain values the e-mail template needs."""
    text = strip_tags(block.text or "")
    return {
        "kind": block.kind,
        "label": block.get_kind_display(),
        "title": block.title,
        "text": Truncator(text).words(34, truncate=" …") if text else "",
        "meta": _meta_for(block),
        "url": _url_for(block),
        "image": _image_for(block),
    }


def render_issue(issue, subscriber=None) -> str:
    """The issue as an HTML e-mail, in the issue's own language.

    Without a subscriber — the composer's preview — the unsubscribe link points
    at the sign-up page instead, so the preview never carries somebody's token.
    """
    blocks = [
        flatten(block)
        for block in issue.blocks.select_related("article", "edition", "event", "ad_slot")
        if not block.is_empty
    ]
    unsubscribe = (
        _absolute(subscriber.unsubscribe_url()) if subscriber else f"{site_url()}{reverse('newsletter:unsubscribe_info')}"
    )
    with translation.override(issue.language):
        return render_to_string(
            "newsletter/email.html",
            {
                "issue": issue,
                "blocks": blocks,
                "SITE_NAME": settings.SITE_NAME,
                "site_url": site_url(),
                "unsubscribe_url": unsubscribe,
            },
        )


def plain_text(issue) -> str:
    """A readable fallback for clients that refuse HTML."""
    lines = [issue.subject, ""]
    if issue.intro:
        lines += [strip_tags(issue.intro), ""]
    for block in issue.blocks.select_related("article", "edition", "event", "ad_slot"):
        if block.is_empty:
            continue
        flat = flatten(block)
        lines.append(flat["title"])
        if flat["meta"]:
            lines.append(flat["meta"])
        if flat["text"]:
            lines.append(flat["text"])
        lines += [flat["url"], ""]
    return "\n".join(lines).strip()
