from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import Edition, EditionContent, ArchiveYear
from .serializers import (
    EditionSerializer, 
    EditionContentSerializer,
    ArchiveYearSerializer
)
from source.utils.archive_utils import ArchiveManager

class ArchiveAPIViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['publication_date', 'title']
    
    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced search endpoint with filtering"""
        query = request.query_params.get('q', '')
        year = request.query_params.get('year')
        categories = request.query_params.getlist('categories')
        content_type = request.query_params.get('content_type')
        language = request.query_params.get('language')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        is_digitized = request.query_params.get('is_digitized')
        
        # Convert is_digitized to boolean if present
        if is_digitized is not None:
            is_digitized = is_digitized.lower() == 'true'
        
        # Use ArchiveManager to perform search
        results = ArchiveManager.search_archive_content(
            query=query,
            year=year,
            categories=categories,
            content_type=content_type,
            language=language,
            start_date=start_date,
            end_date=end_date,
            is_digitized=is_digitized
        )
        
        # Paginate results
        page = self.paginate_queryset(results['results'])
        if page is not None:
            serializer = EditionContentSerializer(page, many=True)
            return self.get_paginated_response({
                'results': serializer.data,
                'statistics': results['statistics']
            })
        
        serializer = EditionContentSerializer(results['results'], many=True)
        return Response({
            'results': serializer.data,
            'statistics': results['statistics']
        })
    
    @method_decorator(cache_page(60 * 60))  # Cache for 1 hour
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get archive summary statistics"""
        cache_key = 'archive_summary'
        summary = cache.get(cache_key)
        
        if not summary:
            start_year = request.query_params.get('start_year')
            end_year = request.query_params.get('end_year')
            
            summary = ArchiveManager.get_archive_summary(
                start_year=start_year,
                end_year=end_year
            )
            
            # Cache the summary
            cache.set(cache_key, summary, timeout=60 * 60)  # 1 hour
        
        return Response(summary)
    
    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    @action(detail=True, methods=['get'])
    def related_content(self, request, pk=None):
        """Get related content for an edition"""
        content = self.get_object()
        max_results = int(request.query_params.get('max_results', 5))
        
        related = ArchiveManager.get_related_content(
            content=content,
            max_results=max_results
        )
        
        serializer = EditionContentSerializer(related, many=True)
        return Response(serializer.data)
