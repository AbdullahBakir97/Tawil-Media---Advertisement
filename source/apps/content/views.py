from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from .models import Article, Category, Magazine


class ArticleListView(ListView):
    template_name = "content/article_list.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        queryset = Article.objects.published().select_related("author").prefetch_related("categories", "tags")
        if slug := self.kwargs.get("slug"):
            self.category = get_object_or_404(Category.objects.active(), slug=slug)
            queryset = queryset.filter(categories=self.category)
        if tag := self.kwargs.get("tag"):
            queryset = queryset.filter(tags__slug=tag).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.active()
        context["category"] = getattr(self, "category", None)
        context["tag"] = self.kwargs.get("tag")
        return context


class ArticleDetailView(DetailView):
    template_name = "content/article_detail.html"
    context_object_name = "article"

    def get_queryset(self):
        """Everything is fetched; `get_object` decides who may see an unpublished
        piece, so a preview link works for someone without an account."""
        return Article.objects.select_related("author").prefetch_related("categories", "tags", "media")

    def get_object(self, queryset=None):
        article = super().get_object(queryset)
        if not article.can_be_seen_by(self.request):
            raise Http404
        return article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object
        context["is_preview"] = not article.is_published
        context["related_articles"] = (
            Article.objects.published()
            .filter(categories__in=article.categories.all())
            .exclude(pk=article.pk)
            .distinct()[:4]
        )
        return context


class MagazineListView(ListView):
    template_name = "content/magazine_list.html"
    context_object_name = "magazines"
    paginate_by = 12

    def get_queryset(self):
        return Magazine.objects.published().select_related("cover_image")


class MagazineDetailView(DetailView):
    template_name = "content/magazine_detail.html"
    context_object_name = "magazine"

    def get_queryset(self):
        return Magazine.objects.select_related("cover_image").prefetch_related("articles")

    def get_object(self, queryset=None):
        magazine = super().get_object(queryset)
        if not magazine.can_be_seen_by(self.request):
            raise Http404
        return magazine

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_preview"] = not self.object.is_published
        return context
