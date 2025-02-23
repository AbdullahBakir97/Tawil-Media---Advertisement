from django.db.models import Q
from django.utils import timezone
from source.apps.content.models import Article, Magazine
from source.apps.archives.models import Edition, EditionContent

class GlobalSearchManager:
    """Manager class to handle global search across all content types"""

    @staticmethod
    def search_content(query, content_type=None, categories=None, start_date=None, end_date=None, max_results=None):
        """
        Search across all content types (articles, magazines, archives)
        """
        results = {
            'articles': [],
            'magazines': [],
            'archives': [],
            'statistics': {
                'total_results': 0,
                'article_count': 0,
                'magazine_count': 0,
                'archive_count': 0
            }
        }

        # Apply date filters
        date_filters = {}
        if start_date:
            date_filters['published_at__gte'] = start_date
        if end_date:
            date_filters['published_at__lte'] = end_date

        # Search articles
        if not content_type or content_type == 'article':
            article_query = Q(title__icontains=query) | Q(content__icontains=query)
            if categories:
                article_query &= Q(categories__in=categories)
            
            articles = Article.objects.published().filter(
                article_query,
                **date_filters
            ).distinct()
            
            if max_results:
                articles = articles[:max_results]
            
            results['articles'] = articles
            results['statistics']['article_count'] = articles.count()

        # Search magazines
        if not content_type or content_type == 'magazine':
            magazine_query = Q(title__icontains=query) | Q(description__icontains=query)
            magazines = Magazine.objects.published().filter(
                magazine_query,
                **date_filters
            ).distinct()
            
            if max_results:
                magazines = magazines[:max_results]
            
            results['magazines'] = magazines
            results['statistics']['magazine_count'] = magazines.count()

        # Search archives using ArchiveManager
        if not content_type or content_type == 'archive':
            from source.utils.archive_utils import ArchiveManager
            archive_results = ArchiveManager.search_archive_content(
                query=query,
                categories=categories,
                start_date=start_date,
                end_date=end_date,
                max_results=max_results
            )
            results['archives'] = archive_results['results']
            results['statistics']['archive_count'] = len(archive_results['results'])

        # Calculate total results
        results['statistics']['total_results'] = (
            results['statistics']['article_count'] +
            results['statistics']['magazine_count'] +
            results['statistics']['archive_count']
        )

        return results

    @staticmethod
    def get_search_suggestions(query, max_results=5):
        """
        Get quick search suggestions across all content types
        """
        suggestions = []

        # Get article suggestions
        article_suggestions = Article.objects.published().filter(
            Q(title__icontains=query)
        )[:max_results]

        for article in article_suggestions:
            suggestions.append({
                'id': f'article_{article.id}',
                'title': article.title,
                'type': 'article',
                'url': article.get_absolute_url(),
                'thumbnail': article.get_thumbnail_url() if hasattr(article, 'get_thumbnail_url') else None
            })

        # Get magazine suggestions if we still have room
        remaining = max_results - len(suggestions)
        if remaining > 0:
            magazine_suggestions = Magazine.objects.published().filter(
                Q(title__icontains=query)
            )[:remaining]

            for magazine in magazine_suggestions:
                suggestions.append({
                    'id': f'magazine_{magazine.id}',
                    'title': magazine.title,
                    'type': 'magazine',
                    'url': magazine.get_absolute_url(),
                    'thumbnail': magazine.cover_image.url if magazine.cover_image else None
                })

        # Get archive suggestions if we still have room
        remaining = max_results - len(suggestions)
        if remaining > 0:
            from source.utils.archive_utils import ArchiveManager
            archive_results = ArchiveManager.search_archive_content(
                query=query,
                max_results=remaining,
                quick_search=True
            )

            for content in archive_results['results']:
                suggestions.append({
                    'id': f'archive_{content.id}',
                    'title': content.title,
                    'type': 'archive',
                    'url': content.get_absolute_url(),
                    'thumbnail': content.get_thumbnail_url() if hasattr(content, 'get_thumbnail_url') else None
                })

        return suggestions
