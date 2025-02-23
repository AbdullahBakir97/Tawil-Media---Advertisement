from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Article, Magazine

def article_list(request):
    """List view for articles"""
    articles = Article.objects.published().order_by('-published_at')
    
    # Handle pagination
    paginator = Paginator(articles, 12)  # 12 articles per page
    page = request.GET.get('page', 1)
    articles = paginator.get_page(page)
    
    context = {
        'articles': articles,
        'page_range': paginator.get_elided_page_range(number=page, on_each_side=2, on_ends=1)
    }
    return render(request, 'content/articles/list.html', context)

def article_detail(request, slug):
    """Detail view for a single article"""
    article = Article.objects.get(slug=slug, is_published=True)
    context = {
        'article': article,
        'related_articles': Article.objects.published().exclude(id=article.id)[:3]
    }
    return render(request, 'content/articles/detail.html', context)


def magazine_list(request):
    """List view for magazines"""
    magazines = Magazine.objects.published().order_by('-published_at')
    
    # Handle pagination
    paginator = Paginator(magazines, 9)  # 9 magazines per page
    page = request.GET.get('page', 1)
    magazines = paginator.get_page(page)
    
    context = {
        'magazines': magazines,
        'page_range': paginator.get_elided_page_range(number=page, on_each_side=2, on_ends=1)
    }
    return render(request, 'content/magazines/list.html', context)

def magazine_detail(request, slug):
    """Detail view for a single magazine"""
    magazine = Magazine.objects.get(slug=slug, is_published=True)
    context = {
        'magazine': magazine,
        'articles': magazine.articles.filter(is_published=True),
        'related_magazines': Magazine.objects.published().exclude(id=magazine.id)[:3]
    }
    return render(request, 'content/magazines/detail.html', context)
