from django.urls import include, path

from . import views

search_patterns = (
    [
        path("suggestions/", views.SearchSuggestionsView.as_view(), name="suggestions"),
    ],
    "search",
)

newsletter_patterns = (
    [
        path("subscribe/", views.NewsletterSubscribeView.as_view(), name="subscribe"),
    ],
    "newsletter",
)

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("search/", views.SearchView.as_view(), name="search"),
    path("search/", include(search_patterns)),
    path("newsletter/", include(newsletter_patterns)),
    path("sitemap/", views.SitemapView.as_view(), name="sitemap"),
]

# Simple informational pages. Each renders templates/pages/<slug>.html.
for slug in ("about", "contact", "advertise", "careers", "help", "privacy", "terms", "cookies"):
    urlpatterns.append(path(f"{slug}/", views.StaticPageView.as_view(page=slug), name=slug))
