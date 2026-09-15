from datetime import date

from django.conf import settings


def site(request):
    """Expose site-wide values to every template."""
    return {
        "SITE_NAME": settings.SITE_NAME,
        "DIRECTOR": settings.DIRECTOR,
        "ADVERTISING_STATS": settings.ADVERTISING_STATS,
        "YEARS_ACTIVE": date.today().year - settings.FOUNDED_YEAR,
    }
