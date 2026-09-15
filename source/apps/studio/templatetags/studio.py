import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

from ..models import FAQ, AdSlot, Milestone, Partner, Testimonial

register = template.Library()


@register.inclusion_tag("studio/partials/ad_slot.html")
def ad_slot(key, fmt="leaderboard"):
    """Render the current booking for ``key``; an empty, labelled slot in DEBUG-free production stays hidden."""
    return {"slot": AdSlot.current(key), "key": key, "fmt": fmt}


@register.filter
def emphasise(text):
    """Turn *word* into <em>word</em> for headline accents, escaping everything else."""
    parts = re.split(r"\*(.+?)\*", escape(text or ""))
    out = []
    for i, part in enumerate(parts):
        out.append(f"<em>{part}</em>" if i % 2 else part)
    return mark_safe("".join(out))


@register.simple_tag
def partners():
    return Partner.objects.filter(is_active=True)


@register.simple_tag
def testimonials(limit=3):
    return Testimonial.objects.filter(is_active=True)[:limit]


@register.simple_tag
def faqs(page="help"):
    return FAQ.objects.filter(page=page, is_active=True)


@register.simple_tag
def milestones():
    return Milestone.objects.filter(is_active=True)
