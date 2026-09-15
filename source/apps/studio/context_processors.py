from django.conf import settings

from .models import Announcement, HeroConfig, Theme


def studio(request):
    """Studio values every template may need: hero config, announcements, active theme."""
    theme = Theme.objects.filter(is_default=True).first()
    return {
        "hero": HeroConfig.for_placement("home") if _wants_hero(request) else None,
        "announcements": Announcement.live(),
        "site_theme": theme,
        "studio_enabled": bool(request.user.is_authenticated and request.user.is_staff) or settings.DEBUG,
    }


def _wants_hero(request):
    # Only the home page (any language prefix) renders the hero; skip the query elsewhere.
    path = request.path
    for code, _name in settings.LANGUAGES:
        if path == f"/{code}/":
            return True
    return path == "/" or path.startswith("/studio/") or path.startswith("/design/") or "/design/" in path
