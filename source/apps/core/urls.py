from django.urls import include, path

from source.apps.advertisements.views import AdvertiseView

from . import views

search_patterns = (
    [
        path("suggestions/", views.SearchSuggestionsView.as_view(), name="suggestions"),
    ],
    "search",
)

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("search/", views.SearchView.as_view(), name="search"),
    path("search/", include(search_patterns)),
    path("sitemap/", views.SitemapView.as_view(), name="sitemap"),
    path("design/", views.StyleGuideView.as_view(), name="styleguide"),
    path("advertise/", AdvertiseView.as_view(), name="advertise"),
    path("advertise/", include("source.apps.advertisements.urls", namespace="advertising")),
]

# Simple informational pages. Each renders templates/pages/<slug>.html.
for slug in ("about", "contact", "careers", "help", "privacy", "terms", "cookies"):
    urlpatterns.append(path(f"{slug}/", views.StaticPageView.as_view(page=slug), name=slug))
