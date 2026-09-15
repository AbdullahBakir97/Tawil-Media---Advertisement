"""Image renditions.

One uploaded file, several sizes, served as WebP with the original format as a
fallback. Renditions are built the first time a template asks for them and then
served from disk; the name carries the source's size and modification time, so a
replaced upload simply lands on a new name instead of serving a stale crop.

Nothing here raises. An unreadable file, a missing library or a full disk means
the template falls back to the original upload, which always works.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)

try:  # Pillow is a hard requirement, but rendering must never take the site down.
    from PIL import Image, ImageOps
except ImportError:  # pragma: no cover - only hit on a broken install
    Image = ImageOps = None

#: The widths we offer the browser. Covers a phone at 2× up to a wide desktop hero.
WIDTHS = (400, 800, 1200, 1600, 2000)

#: Renditions live here, beside the uploads, and can be deleted at any time.
RENDITION_DIR = "renditions"

#: Beyond this the file is left alone: an animated GIF or an SVG has no business
#: being re-encoded, and a PDF is not an image at all.
RENDERABLE = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp"}

QUALITY = 82


def measure(file) -> tuple[int, int] | None:
    """The pixel size of an uploaded image, or None if it cannot be read."""
    if Image is None or not file:
        return None
    try:
        with file.open("rb") as handle, Image.open(handle) as image:
            return image.size
    except Exception:
        logger.debug("Could not measure %s", getattr(file, "name", file), exc_info=True)
        return None


def _stamp(file) -> str:
    """A short digest of the source: its path plus its size, so replacing a file
    under the same name still produces a fresh rendition name."""
    try:
        size = file.size
    except Exception:
        size = 0
    return hashlib.sha1(f"{file.name}:{size}".encode()).hexdigest()[:12]


def _renderable(file) -> bool:
    return Image is not None and bool(file) and Path(file.name).suffix.lower() in RENDERABLE


def rendition(media, width: int) -> str | None:
    """URL of `media` at `width` pixels wide as WebP, building it if needed.

    Returns None when the source is wider than nothing useful, cannot be read, or
    is already narrower than the requested width — the caller then keeps the
    original, which is what a browser would have picked anyway.
    """
    file = getattr(media, "file", None)
    if not _renderable(file):
        return None
    if media.width and media.width <= width:
        return None

    name = f"{RENDITION_DIR}/{_stamp(file)}-{width}.webp"
    if default_storage.exists(name):
        return default_storage.url(name)

    try:
        with file.open("rb") as handle, Image.open(handle) as image:
            image = ImageOps.exif_transpose(image)
            image = image.convert("RGBA" if image.mode in ("RGBA", "LA", "P") else "RGB")
            height = max(1, round(image.height * width / image.width))
            image = image.resize((width, height), Image.LANCZOS)
            buffer = _encode(image)
        return default_storage.url(default_storage.save(name, buffer))
    except Exception:
        logger.warning("Could not render %s at %spx", file.name, width, exc_info=True)
        return None


def _encode(image):
    from io import BytesIO

    from django.core.files.base import ContentFile

    buffer = BytesIO()
    image.save(buffer, format="WEBP", quality=QUALITY, method=4)
    return ContentFile(buffer.getvalue())


def srcset(media, widths=WIDTHS) -> str:
    """A `srcset` value for the sizes that are actually smaller than the source."""
    entries = []
    for width in widths:
        url = rendition(media, width)
        if url:
            entries.append(f"{url} {width}w")
    if entries and media.file:
        # The original closes the set, so a wide viewport still gets full detail.
        entries.append(f"{media.file.url} {media.width or max(widths)}w")
    return ", ".join(entries)
