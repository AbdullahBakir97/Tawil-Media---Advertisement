from django.conf import settings
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import ListView, TemplateView

from source.apps.content.models import Article, Category, Magazine


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        articles = Article.objects.published().select_related("author").prefetch_related("categories")
        context["featured_articles"] = articles[:6]
        context["latest_magazines"] = Magazine.objects.published().select_related("cover_image")[:3]
        context["categories"] = Category.objects.active()[:8]
        return context


class StaticPageView(TemplateView):
    """Render an informational page from templates/pages/<page>.html."""

    page = None

    def get_template_names(self):
        return [f"pages/{self.page}.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(settings.CONTACT_DETAILS)
        if self.page == "advertise":
            context.update(settings.ADVERTISING_STATS)
        return context


class SitemapView(TemplateView):
    template_name = "pages/sitemap.html"


class SearchView(ListView):
    template_name = "pages/search.html"
    context_object_name = "results"
    paginate_by = 10

    def get_query(self):
        return self.request.GET.get("q", "").strip()

    def get_queryset(self):
        query = self.get_query()
        if not query:
            return Article.objects.none()
        return (
            Article.objects.published()
            .filter(Q(title__icontains=query) | Q(content__icontains=query))
            .select_related("author")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.get_query()
        return context


class SearchSuggestionsView(ListView):
    """HTMX endpoint returning a small partial with matching article titles."""

    template_name = "partials/search_suggestions.html"
    context_object_name = "suggestions"

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        if len(query) < 2:
            return Article.objects.none()
        return Article.objects.published().filter(title__icontains=query).only("title", "slug")[:5]


def page_not_found(request, exception=None):
    return render(request, "errors/404.html", status=404)


def server_error(request):
    return render(request, "errors/500.html", status=500)
