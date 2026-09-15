from .models import Magazine


def header_magazines(request):
    """Latest published magazines for the home-page header slider (lazy queryset)."""
    return {"header_magazines": Magazine.objects.published().select_related("cover_image")[:3]}
