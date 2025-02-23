from datetime import datetime
from typing import List, Optional, Union, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from source.apps.archives.models import (
    ArchiveYear, Edition, EditionContent, ArchiveMetadata,
    ArchiveCategory, YearCategoryHighlight
)
from source.apps.content.models import Article, Category, Media

class ArchiveService:
    """Service class for handling archive-related operations"""
    
    @classmethod
    @transaction.atomic
    def create_edition(cls, year: int, edition_data: Dict[str, Any]) -> Edition:
        """Create a new edition with validation and related objects"""
        archive_year, _ = ArchiveYear.objects.get_or_create(
            year=year,
            defaults={'description': f'Archive for year {year}'}
        )
        
        edition = Edition.objects.create(
            archive_year=archive_year,
            edition_number=edition_data['edition_number'],
            title=edition_data['title'],
            description=edition_data.get('description', ''),
            edition_type=edition_data.get('edition_type', 'regular'),
            season=edition_data.get('season'),
            publication_date=edition_data['publication_date'],
            is_digitized=edition_data.get('is_digitized', False),
            page_count=edition_data.get('page_count', 0),
            file_size=edition_data.get('file_size', 0)
        )
        
        if 'cover_image' in edition_data:
            edition.cover_image = edition_data['cover_image']
            edition.save()
            
        return edition

    @classmethod
    @transaction.atomic
    def archive_article(cls, article: Article, edition: Edition, page_number: int) -> EditionContent:
        """Archive an existing article into an edition"""
        content = EditionContent.objects.create(
            edition=edition,
            title=article.title,
            content_type='article',
            page_number=page_number,
            content_preview=article.content[:500],
            keywords=article.keywords,
            original_article=article,
            is_searchable=True
        )
        
        # Copy categories
        content.categories.set(article.categories.all())
        
        # Create metadata
        ArchiveMetadata.objects.create(
            edition_content=content,
            language=article.language,
            contributors=article.author.get_full_name(),
            digitization_date=datetime.now().date(),
            preservation_status='excellent'
        )
        
        return content

    @classmethod
    def get_year_statistics(cls, year: int) -> Dict[str, Any]:
        """Get comprehensive statistics for an archive year"""
        try:
            archive_year = ArchiveYear.objects.get(year=year)
        except ArchiveYear.DoesNotExist:
            raise ValidationError(f"Archive year {year} does not exist")
            
        editions = archive_year.editions.all()
        
        return {
            'total_editions': archive_year.total_editions,
            'total_content': EditionContent.objects.filter(edition__archive_year=archive_year).count(),
            'content_by_type': EditionContent.objects.filter(
                edition__archive_year=archive_year
            ).values('content_type').annotate(count=models.Count('id')),
            'digitized_editions': editions.filter(is_digitized=True).count(),
            'total_pages': sum(edition.page_count for edition in editions),
            'categories': Category.objects.filter(
                archived_content__edition__archive_year=archive_year
            ).distinct().count()
        }

    @classmethod
    @transaction.atomic
    def create_category_highlight(
        cls, year: int, category: Category, 
        description: str, featured_content_ids: List[int]
    ) -> YearCategoryHighlight:
        """Create or update a category highlight for a specific year"""
        archive_year = ArchiveYear.objects.get(year=year)
        
        highlight, created = YearCategoryHighlight.objects.get_or_create(
            year=archive_year,
            category=category,
            defaults={'highlight_description': description}
        )
        
        if not created:
            highlight.highlight_description = description
            highlight.save()
            
        if featured_content_ids:
            highlight.featured_content.set(
                EditionContent.objects.filter(id__in=featured_content_ids)
            )
            
        return highlight

    @classmethod
    def search_archive(
        cls, query: str, 
        year: Optional[int] = None,
        content_type: Optional[str] = None,
        category: Optional[Category] = None
    ) -> List[EditionContent]:
        """Search through archived content with various filters"""
        queryset = EditionContent.objects.select_related(
            'edition', 'edition__archive_year'
        ).prefetch_related('categories')
        
        if query:
            queryset = queryset.filter(
                models.Q(title__icontains=query) |
                models.Q(content_preview__icontains=query) |
                models.Q(keywords__icontains=query)
            )
            
        if year:
            queryset = queryset.filter(edition__archive_year__year=year)
            
        if content_type:
            queryset = queryset.filter(content_type=content_type)
            
        if category:
            queryset = queryset.filter(categories=category)
            
        return queryset.order_by('-edition__publication_date')

    @classmethod
    @transaction.atomic
    def bulk_update_metadata(
        cls, content_ids: List[int], 
        metadata: Dict[str, Any]
    ) -> int:
        """Bulk update metadata for multiple content items"""
        updated = 0
        for content in EditionContent.objects.filter(id__in=content_ids):
            try:
                content_metadata = content.metadata
                for key, value in metadata.items():
                    if hasattr(content_metadata, key):
                        setattr(content_metadata, key, value)
                content_metadata.save()
                updated += 1
            except ArchiveMetadata.DoesNotExist:
                continue
        return updated

    @classmethod
    def get_category_timeline(
        cls, category: Category, 
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> Dict[int, Dict[str, Any]]:
        """Get a timeline of content for a specific category"""
        queryset = EditionContent.objects.filter(
            categories=category
        ).select_related('edition__archive_year')
        
        if start_year:
            queryset = queryset.filter(edition__archive_year__year__gte=start_year)
        if end_year:
            queryset = queryset.filter(edition__archive_year__year__lte=end_year)
            
        timeline = {}
        for content in queryset:
            year = content.edition.archive_year.year
            if year not in timeline:
                timeline[year] = {
                    'total_content': 0,
                    'content_types': {},
                    'editions': set()
                }
            
            timeline[year]['total_content'] += 1
            timeline[year]['editions'].add(content.edition.edition_number)
            
            content_type = content.content_type
            if content_type not in timeline[year]['content_types']:
                timeline[year]['content_types'][content_type] = 0
            timeline[year]['content_types'][content_type] += 1
            
        # Convert sets to lists for JSON serialization
        for year_data in timeline.values():
            year_data['editions'] = sorted(list(year_data['editions']))
            
        return timeline
