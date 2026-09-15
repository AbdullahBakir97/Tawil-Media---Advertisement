"""Template tags for pictures.

    {% picture article.cover sizes="(min-width: 64rem) 33vw, 100vw" class="card-img" %}

renders a responsive `<picture>`: WebP renditions in a srcset, the original as the
fallback, the intrinsic width and height so the layout never jumps, and the focal
point as `object-position` so a crop keeps the subject in frame.
"""

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from ..imaging import srcset

register = template.Library()

DEFAULT_SIZES = "(min-width: 64rem) 50vw, 100vw"


@register.simple_tag
def picture(media, sizes=DEFAULT_SIZES, css_class="", alt=None, loading="lazy", fetchpriority=""):
    """A responsive picture for a Media object. Renders nothing without one."""
    if not media or not getattr(media, "file", None):
        return ""

    attrs = [
        format_html('src="{}"', media.file.url),
        format_html('alt="{}"', media.alt_text if alt is None else alt),
        format_html('loading="{}"', loading),
        'decoding="async"',
    ]
    if css_class:
        attrs.append(format_html('class="{}"', css_class))
    if media.width and media.height:
        attrs.append(format_html('width="{}" height="{}"', media.width, media.height))
    if fetchpriority:
        attrs.append(format_html('fetchpriority="{}"', fetchpriority))
    position = getattr(media, "object_position", None)
    if position and position != "50% 50%":
        attrs.append(format_html('style="object-position:{}"', position))

    candidates = srcset(media)
    if candidates:
        attrs.append(format_html('srcset="{}" sizes="{}"', candidates, sizes))

    return mark_safe(f"<img {' '.join(attrs)}>")  # noqa: S308 - every part is escaped above


@register.simple_tag
def focal_style(media):
    """`object-position` for markup that builds its own <img>."""
    position = getattr(media, "object_position", None)
    return format_html('style="object-position:{}"', position) if position else ""
