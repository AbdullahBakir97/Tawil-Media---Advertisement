from rest_framework import serializers
from .models import (
    Edition, EditionContent, ArchiveYear, ArchiveMetadata,
    ArchiveCategory, YearCategoryHighlight
)
from source.apps.content.models import Category, Media

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id', 'file', 'media_type', 'alt_text']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']

class ArchiveMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchiveMetadata
        fields = [
            'language', 'contributors', 'source_info',
            'digitization_date', 'preservation_status',
            'copyright_info', 'tags'
        ]

class EditionContentSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    metadata = ArchiveMetadataSerializer(read_only=True)
    
    class Meta:
        model = EditionContent
        fields = [
            'id', 'title', 'content_type', 'page_number',
            'digital_content', 'content_preview', 'keywords',
            'is_searchable', 'categories', 'metadata'
        ]

class EditionSerializer(serializers.ModelSerializer):
    cover_image = MediaSerializer(read_only=True)
    primary_category = CategorySerializer(read_only=True)
    contents = EditionContentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Edition
        fields = [
            'id', 'edition_number', 'title', 'slug',
            'description', 'edition_type', 'season',
            'publication_date', 'cover_image', 'is_digitized',
            'page_count', 'file_size', 'primary_category',
            'contents'
        ]

class ArchiveYearSerializer(serializers.ModelSerializer):
    editions = EditionSerializer(many=True, read_only=True)
    
    class Meta:
        model = ArchiveYear
        fields = ['year', 'description', 'total_editions', 'editions']

class YearCategoryHighlightSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    featured_content = EditionContentSerializer(many=True, read_only=True)
    
    class Meta:
        model = YearCategoryHighlight
        fields = [
            'category', 'highlight_description',
            'display_order', 'featured_content'
        ]
