from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Count
from .models import Edition, EditionContent

def test_chart_view(request):
    """Test view for Chart.js integration"""
    return render(request, 'content/archives/test-chart.html')

def browse_view(request):
    """Main archive browse view"""
    context = {
        'categories': ['News', 'Culture', 'Business', 'Technology']  # Replace with actual categories from your model
    }
    return render(request, 'content/archives/browse.html', context)

@require_http_methods(["GET"])
def archive_search_api(request):
    """API endpoint for searching archives"""
    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    filters = {
        'year': request.GET.get('year'),
        'categories': request.GET.getlist('categories'),
        'content_type': request.GET.get('contentType'),
        'language': request.GET.get('language'),
        'is_digitized': request.GET.get('isDigitized')
    }
    
    # Mock data for testing - replace with actual database query
    results = [
        {
            'id': 1,
            'title': 'Sample Magazine Issue',
            'description': 'This is a sample magazine issue from our archives.',
            'thumbnail': '/static/img/sample-thumb.jpg',
            'date': '2024-01-01',
            'type': 'magazine',
            'categories': ['News', 'Culture']
        }
    ] * 10  # Duplicate for testing
    
    paginator = Paginator(results, 12)
    page_obj = paginator.get_page(page)
    
    return JsonResponse({
        'results': list(page_obj),
        'has_next': page_obj.has_next(),
        'total_pages': paginator.num_pages,
        'current_page': page,
        'total_results': paginator.count
    })

@require_http_methods(["GET"])
def archive_summary_api(request):
    """API endpoint for archive statistics"""
    # Mock data for testing - replace with actual database queries
    summary = {
        'total_items': 1000,
        'digitized_count': 750,
        'category_count': 8,
        'year_range': {'start': 1950, 'end': 2024},
        'category_distribution': [
            {'categories__name': 'News', 'content_count': 300},
            {'categories__name': 'Culture', 'content_count': 250},
            {'categories__name': 'Business', 'content_count': 200},
            {'categories__name': 'Technology', 'content_count': 150}
        ],
        'content_type_distribution': [
            {'content_type': 'Magazine', 'type_count': 400},
            {'content_type': 'Article', 'type_count': 300},
            {'content_type': 'Image', 'type_count': 200},
            {'content_type': 'Document', 'type_count': 100}
        ]
    }
    
    return JsonResponse(summary)
