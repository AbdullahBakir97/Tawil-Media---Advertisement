"""Root URL configuration.

Public pages live under a language prefix (/de/, /ar/, /en/); the default
language (German) is served without a prefix. Admin and the language switcher
stay unprefixed.
"""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(
    path("", include("source.apps.core.urls")),
    path("accounts/", include("source.apps.users.urls")),
    path("articles/", include("source.apps.content.urls.articles", namespace="articles")),
    path("authors/", include("source.apps.content.urls.authors", namespace="authors")),
    path("magazines/", include("source.apps.content.urls.magazines", namespace="magazines")),
    path("archives/", include("source.apps.archives.urls", namespace="archives")),
    path("newsletter/", include("source.apps.newsletter.urls", namespace="newsletter")),
    path("notifications/", include("source.apps.notifications.urls", namespace="notifications")),
    path("studio/", include("source.apps.studio.urls", namespace="studio")),
    prefix_default_language=False,
)

if settings.DEBUG:
    # Django's staticfiles app already serves STATIC_URL in DEBUG; media needs this.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "source.apps.core.views.page_not_found"
handler500 = "source.apps.core.views.server_error"
