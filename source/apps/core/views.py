from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
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
        context["show_hero"] = True
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


class StyleGuideView(UserPassesTestMixin, TemplateView):
    """The Atlas: a visual map of every page, token, component, pattern and motion
    preset in the project, plus live hero proposals. Staff only, or anyone while DEBUG is on."""

    template_name = "pages/atlas/index.html"
    raise_exception = False

    def test_func(self):
        return settings.DEBUG or self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["atlas_magazines"] = list(Magazine.objects.published().select_related("cover_image")[:3])
        context["atlas_articles"] = list(
            Article.objects.published().select_related("author").prefetch_related("categories")[:4]
        )
        return context


class SitemapView(TemplateView):
    template_name = "pages/sitemap.html"



def article_search(query, headlines_only=False):
    """Match a search term against every language an article is written in.

    A reader searching in Arabic must find the Arabic headline, not only the
    desk's own working title, so each translated field is searched alongside it.
    """
    fields = ["title", "title_de", "title_ar", "title_en"]
    if not headlines_only:
        fields += ["content", "content_de", "content_ar", "content_en",
                   "standfirst_de", "standfirst_ar", "standfirst_en"]
    condition = Q()
    for field in fields:
        condition |= Q(**{f"{field}__icontains": query})
    return condition


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
            .filter(article_search(query))
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
        return (
            Article.objects.published()
            .filter(article_search(query, headlines_only=True))
            .only("title", "title_de", "title_ar", "title_en", "slug")[:5]
        )


def page_not_found(request, exception=None):
    return render(request, "errors/404.html", status=404)


def server_error(request):
    return render(request, "errors/500.html", status=500)
