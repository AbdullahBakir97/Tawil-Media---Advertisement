from .models import Magazine


def header_magazines(request):
    """Latest published magazines for the home-page header slider (lazy queryset)."""
    published = Magazine.objects.published()
    return {
        "header_magazines": published.select_related("cover_image")[:3],
        "magazine_count": published.count,
    }
