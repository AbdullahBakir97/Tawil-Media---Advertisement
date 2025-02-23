from datetime import datetime
from typing import List, Optional, Dict, Any
from django.db.models import Q, Count
from django.core.files import File
from django.utils import timezone
from source.apps.archives.models import (
    ArchiveYear, Edition, EditionContent, ArchiveMetadata,
    ArchiveCategory, YearCategoryHighlight
)
from source.apps.content.models import Category, Media
from source.utils.indesign_handler import InDesignHandler

class ArchiveManager:
    """Utility class for managing archive operations"""
    
    @staticmethod
    def create_or_update_edition(
        year: int,
        edition_number: int,
        title: str,
        publication_date: datetime,
        description: str = "",
        edition_type: str = "regular",
        season: Optional[str] = None,
        cover_image: Optional[Media] = None,
        primary_category: Optional[Category] = None
    ) -> Edition:
        """Create or update an edition in the archive"""
        archive_year, _ = ArchiveYear.objects.get_or_create(
            year=year,
            defaults={"description": f"Archive for year {year}"}
        )
        
        edition, created = Edition.objects.get_or_create(
            archive_year=archive_year,
            edition_number=edition_number,
            defaults={
                "title": title,
                "publication_date": publication_date,
                "description": description,
                "edition_type": edition_type,
                "season": season,
                "cover_image": cover_image,
                "primary_category": primary_category
            }
        )
        
        if not created:
            edition.title = title
            edition.publication_date = publication_date
            edition.description = description
            edition.edition_type = edition_type
            edition.season = season
            if cover_image:
                edition.cover_image = cover_image
            if primary_category:
                edition.primary_category = primary_category
            edition.save()
            
        return edition

    @staticmethod
    def add_edition_content(
        edition: Edition,
        title: str,
        page_number: int,
        content_type: str,
        categories: List[Category],
        digital_content: Optional[File] = None,
        content_preview: str = "",
        keywords: str = "",
        is_searchable: bool = True
    ) -> EditionContent:
        """Add content to an edition"""
        content = EditionContent.objects.create(
            edition=edition,
            title=title,
            page_number=page_number,
            content_type=content_type,
            digital_content=digital_content,
            content_preview=content_preview,
            keywords=keywords,
            is_searchable=is_searchable
        )
        content.categories.set(categories)
        return content

    @staticmethod
    def create_metadata(
        edition_content: EditionContent,
        language: str = "ar",
        contributors: str = "",
        source_info: str = "",
        digitization_date: Optional[datetime] = None,
        digitization_notes: str = "",
        preservation_status: str = "good",
        copyright_info: str = "",
        tags: str = ""
    ) -> ArchiveMetadata:
        """Create metadata for edition content"""
        metadata, _ = ArchiveMetadata.objects.get_or_create(
            edition_content=edition_content,
            defaults={
                "language": language,
                "contributors": contributors,
                "source_info": source_info,
                "digitization_date": digitization_date or timezone.now().date(),
                "digitization_notes": digitization_notes,
                "preservation_status": preservation_status,
                "copyright_info": copyright_info,
                "tags": tags
            }
        )
        return metadata

    @staticmethod
    def process_indesign_edition(
        indesign_file_path: str,
        year: int,
        edition_number: int,
        title: str,
        publication_date: datetime,
        categories: List[Category],
        **edition_kwargs
    ) -> Edition:
        """Process an InDesign file and create an edition with its contents"""
        # Create edition
        edition = ArchiveManager.create_or_update_edition(
            year=year,
            edition_number=edition_number,
            title=title,
            publication_date=publication_date,
            **edition_kwargs
        )
        
        # Process InDesign file
        handler = InDesignHandler()
        processed_data = handler.process_file(indesign_file_path)
        
        # Update edition with processed data
        edition.page_count = processed_data.get("page_count", 0)
        edition.file_size = processed_data.get("file_size", 0)
        edition.is_digitized = True
        
        if processed_data.get("cover_image"):
            edition.cover_image = processed_data["cover_image"]
        
        edition.save()
        
        # Create content entries for each page
        for page_data in processed_data.get("pages", []):
            content = ArchiveManager.add_edition_content(
                edition=edition,
                title=f"Page {page_data['page_number']}",
                page_number=page_data["page_number"],
                content_type="article",
                categories=categories,
                digital_content=page_data.get("digital_content"),
                content_preview=page_data.get("preview", ""),
                keywords=page_data.get("keywords", ""),
            )
            
            # Create metadata for the content
            ArchiveManager.create_metadata(
                edition_content=content,
                digitization_notes=f"Processed from InDesign file: {indesign_file_path}",
                digitization_date=timezone.now().date()
            )
            
        return edition

    @staticmethod
    def get_edition_statistics(edition: Edition) -> Dict[str, Any]:
        """Get statistics for an edition"""
        content_stats = edition.contents.aggregate(
            total_content=Count('id'),
            searchable_content=Count('id', filter=Q(is_searchable=True)),
            articles=Count('id', filter=Q(content_type='article')),
            editorials=Count('id', filter=Q(content_type='editorial')),
            interviews=Count('id', filter=Q(content_type='interview')),
            galleries=Count('id', filter=Q(content_type='gallery')),
            advertisements=Count('id', filter=Q(content_type='advertisement'))
        )
        
        category_stats = {}
        for category in edition.contents.values('categories__name').annotate(count=Count('id')):
            if category['categories__name']:
                category_stats[category['categories__name']] = category['count']
        
        return {
            "content_statistics": content_stats,
            "category_statistics": category_stats,
            "total_pages": edition.page_count,
            "file_size_mb": round(edition.file_size / (1024 * 1024), 2),
            "digitization_status": "Digitized" if edition.is_digitized else "Not Digitized"
        }

    @staticmethod
    def update_year_highlights(
        year: ArchiveYear,
        category: Category,
        featured_content: List[EditionContent],
        highlight_description: str = "",
        display_order: int = 0
    ) -> YearCategoryHighlight:
        """Update category highlights for a specific year"""
        highlight, _ = YearCategoryHighlight.objects.get_or_create(
            year=year,
            category=category,
            defaults={
                "highlight_description": highlight_description,
                "display_order": display_order
            }
        )
        
        highlight.featured_content.set(featured_content)
        return highlight

    @staticmethod
    def search_archive_content(
        query: str,
        year: Optional[int] = None,
        categories: Optional[List[Category]] = None,
        content_type: Optional[str] = None,
        language: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        is_digitized: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Search through archived content with various filters"""
        content_query = EditionContent.objects.all()
        
        # Apply filters
        if query:
            content_query = content_query.filter(
                Q(title__icontains=query) |
                Q(content_preview__icontains=query) |
                Q(keywords__icontains=query)
            )
        
        if year:
            content_query = content_query.filter(edition__archive_year__year=year)
            
        if categories:
            content_query = content_query.filter(categories__in=categories)
            
        if content_type:
            content_query = content_query.filter(content_type=content_type)
            
        if language:
            content_query = content_query.filter(metadata__language=language)
            
        if start_date:
            content_query = content_query.filter(edition__publication_date__gte=start_date)
            
        if end_date:
            content_query = content_query.filter(edition__publication_date__lte=end_date)
            
        if is_digitized is not None:
            content_query = content_query.filter(edition__is_digitized=is_digitized)
        
        # Get aggregated statistics
        stats = content_query.aggregate(
            total_results=Count('id'),
            unique_editions=Count('edition', distinct=True),
            unique_years=Count('edition__archive_year', distinct=True)
        )
        
        return {
            "results": content_query.select_related('edition', 'metadata').prefetch_related('categories'),
            "statistics": stats
        }

    @staticmethod
    def get_archive_summary(
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get a summary of the archive contents"""
        years_query = ArchiveYear.objects.all()
        
        if start_year:
            years_query = years_query.filter(year__gte=start_year)
        if end_year:
            years_query = years_query.filter(year__lte=end_year)
            
        years_query = years_query.annotate(
            total_editions=Count('editions'),
            total_content=Count('editions__contents'),
            digitized_editions=Count('editions', filter=Q(editions__is_digitized=True))
        )
        
        category_stats = EditionContent.objects.values(
            'categories__name'
        ).annotate(
            content_count=Count('id')
        ).order_by('-content_count')
        
        content_type_stats = EditionContent.objects.values(
            'content_type'
        ).annotate(
            type_count=Count('id')
        ).order_by('-type_count')
        
        return {
            "years": years_query,
            "category_distribution": category_stats,
            "content_type_distribution": content_type_stats,
            "total_years": years_query.count(),
            "total_editions": sum(year.total_editions for year in years_query),
            "total_digitized": sum(year.digitized_editions for year in years_query)
        }

    @staticmethod
    def bulk_update_metadata(
        content_ids: List[int],
        metadata_updates: Dict[str, Any]
    ) -> int:
        """Bulk update metadata for multiple content items"""
        valid_fields = {
            'language', 'contributors', 'source_info',
            'digitization_notes', 'preservation_status',
            'copyright_info', 'tags'
        }
        
        # Filter out invalid fields
        updates = {k: v for k, v in metadata_updates.items() if k in valid_fields}
        
        if not updates:
            return 0
            
        return ArchiveMetadata.objects.filter(
            edition_content_id__in=content_ids
        ).update(**updates)

    @staticmethod
    def get_related_content(
        content: EditionContent,
        max_results: int = 5
    ) -> List[EditionContent]:
        """Find related content based on categories and keywords"""
        categories = content.categories.all()
        
        related = EditionContent.objects.filter(
            categories__in=categories
        ).exclude(
            id=content.id
        ).annotate(
            relevance=Count('categories', filter=Q(categories__in=categories))
        ).order_by('-relevance')
        
        # If keywords exist, boost results that share keywords
        if content.keywords:
            keywords = content.keywords.split(',')
            keyword_filter = Q()
            for keyword in keywords:
                keyword = keyword.strip()
                if keyword:
                    keyword_filter |= Q(keywords__icontains=keyword)
                    
            related = related.filter(keyword_filter)
            
        return related[:max_results]