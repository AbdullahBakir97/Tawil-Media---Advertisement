"""Root URL configuration."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("source.apps.core.urls")),
    path("accounts/", include("source.apps.users.urls")),
    path("articles/", include("source.apps.content.urls.articles", namespace="articles")),
    path("magazines/", include("source.apps.content.urls.magazines", namespace="magazines")),
    path("archives/", include("source.apps.archives.urls", namespace="archives")),
]

if settings.DEBUG:
    # Django's staticfiles app already serves STATIC_URL in DEBUG; media needs this.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "source.apps.core.views.page_not_found"
handler500 = "source.apps.core.views.server_error"
