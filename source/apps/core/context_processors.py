from django.conf import settings


def site(request):
    """Expose site-wide values to every template."""
    return {"SITE_NAME": settings.SITE_NAME}
