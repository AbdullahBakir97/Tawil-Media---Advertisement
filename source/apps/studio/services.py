"""Render an edition's PDF into page images for the flip-book reader."""

import io
import logging

from django.core.files.base import ContentFile

from .models import MagazinePage

log = logging.getLogger(__name__)

PAGE_WIDTH = 1400  # px, long enough for a two-page spread on a 4K screen
THUMB_WIDTH = 200


def render_magazine_pages(magazine, *, replace=True):
    """Rasterise every page of ``magazine.pdf`` into MagazinePage rows. Returns the page count."""
    if not magazine.pdf:
        return 0
    try:
        import pymupdf as fitz
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("PyMuPDF is required to render magazine pages: pip install pymupdf") from exc

    if replace:
        magazine.pages.all().delete()

    magazine.pdf.open("rb")
    try:
        doc = fitz.open(stream=magazine.pdf.read(), filetype="pdf")
    finally:
        magazine.pdf.close()

    count = 0
    for index, page in enumerate(doc, start=1):
        zoom = PAGE_WIDTH / page.rect.width
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        image = ContentFile(pix.tobytes("jpeg", jpg_quality=82), name=f"{magazine.slug}-{index:03d}.jpg")
        thumb_zoom = THUMB_WIDTH / page.rect.width
        thumb_pix = page.get_pixmap(matrix=fitz.Matrix(thumb_zoom, thumb_zoom), alpha=False)
        thumb = ContentFile(thumb_pix.tobytes("jpeg", jpg_quality=70), name=f"{magazine.slug}-{index:03d}-thumb.jpg")
        MagazinePage.objects.create(
            magazine=magazine, number=index, image=image, thumbnail=thumb, width=pix.width, height=pix.height
        )
        count += 1
    doc.close()
    type(magazine).objects.filter(pk=magazine.pk).update(pdf_rendered=magazine.pdf.name)
    magazine.pdf_rendered = magazine.pdf.name
    log.info("Rendered %s pages for %s", count, magazine)
    return count


def make_thumbnail(pdf_bytes):  # pragma: no cover - helper for admin previews
    import pymupdf as fitz

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pix = doc[0].get_pixmap(matrix=fitz.Matrix(0.5, 0.5), alpha=False)
    buffer = io.BytesIO(pix.tobytes("jpeg"))
    doc.close()
    return buffer
