from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from .managers import GlobalSearchManager
from django.contrib.auth import login
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required

# Create your views here.

def home_view(request):
    """Home page view."""
    return render(request, 'content/core/home.html')

def about_view(request):
    """About page view."""
    return render(request, 'core/pages/about.html')

def contact_view(request):
    """Contact page view."""
    return render(request, 'core/pages/contact.html', {
        'company_address': {
            'street': '123 Media Street',
            'city': 'Dubai',
            'country': 'UAE',
            'postal_code': '12345'
        },
        'contact_email': 'contact@tawilmedia.com',
        'contact_phone': '+971 123 456 789'
    })

def advertise_view(request):
    """Advertise page view."""
    return render(request, 'core/pages/advertise.html', {
        'monthly_readers': '500K+',
        'engagement_rate': '85%',
        'industry_reach': '20+'
    })

def help_view(request):
    """Help center page view."""
    return render(request, 'core/pages/help.html')

def careers_view(request):
    """Careers page view."""
    return render(request, 'core/pages/careers.html')

def cookies_view(request):
    """Cookie policy page view."""
    return render(request, 'core/pages/cookies.html')

def sitemap_view(request):
    """Sitemap page view."""
    return render(request, 'content/core/pages/sitemap.html')

def search_view(request):
    """Global search view."""
    query = request.GET.get('q', '')
    content_type = request.GET.get('type')
    categories = request.GET.getlist('categories')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    page = int(request.GET.get('page', 1))
    
    # Perform search
    results = GlobalSearchManager.search_content(
        query=query,
        content_type=content_type,
        categories=categories,
        start_date=start_date,
        end_date=end_date
    )
    
    # Prepare results for template
    all_results = []
    
    # Combine and format results from different content types
    for article in results['articles']:
        all_results.append({
            'id': f'article_{article.id}',
            'title': article.title,
            'type': 'article',
            'url': article.get_absolute_url(),
            'thumbnail': article.get_thumbnail_url() if hasattr(article, 'get_thumbnail_url') else None,
            'description': article.content[:200] + '...' if len(article.content) > 200 else article.content,
            'date': article.published_at,
            'categories': [cat.name for cat in article.categories.all()]
        })
    
    for magazine in results['magazines']:
        all_results.append({
            'id': f'magazine_{magazine.id}',
            'title': magazine.title,
            'type': 'magazine',
            'url': magazine.get_absolute_url(),
            'thumbnail': magazine.cover_image.url if magazine.cover_image else None,
            'description': magazine.description[:200] + '...' if len(magazine.description) > 200 else magazine.description,
            'date': magazine.published_at,
            'articles_count': magazine.articles.count()
        })
    
    for archive in results['archives']:
        all_results.append({
            'id': f'archive_{archive.id}',
            'title': archive.title,
            'type': 'archive',
            'url': archive.get_absolute_url(),
            'thumbnail': archive.get_thumbnail_url() if hasattr(archive, 'get_thumbnail_url') else None,
            'description': archive.content_preview[:200] + '...' if len(archive.content_preview) > 200 else archive.content_preview,
            'date': archive.edition.publication_date,
            'edition': archive.edition.title,
            'categories': [cat.name for cat in archive.categories.all()]
        })
    
    # Paginate results
    paginator = Paginator(all_results, 12)  # 12 items per page
    page_obj = paginator.get_page(page)
    
    context = {
        'query': query,
        'content_type': content_type,
        'categories': categories,
        'start_date': start_date,
        'end_date': end_date,
        'results': page_obj,
        'statistics': results['statistics'],
        'page_range': paginator.get_elided_page_range(page, on_each_side=2, on_ends=1)
    }
    
    return render(request, 'core/search.html', context)

def search_suggestions_view(request):
    """AJAX view for search suggestions."""
    query = request.GET.get('q', '')
    max_results = int(request.GET.get('max_results', 5))
    
    suggestions = GlobalSearchManager.get_search_suggestions(
        query=query,
        max_results=max_results
    )
    
    return JsonResponse({'suggestions': suggestions})

def terms_view(request):
    """View for Terms of Service page."""
    return render(request, 'core/pages/terms.html')

def privacy_view(request):
    """View for Privacy Policy page."""
    return render(request, 'core/pages/privacy.html')

@login_required
def profile_view(request):
    """User profile view."""
    return render(request, 'content/core/profile.html', {
        'user': request.user,
        'profile': request.user.userprofile
    })

@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            
            # Handle HTMX request
            if request.headers.get('HX-Request'):
                response = JsonResponse({'redirect': '/'})
                response['HX-Redirect'] = '/'
                return response
            
            return redirect('core:home')
        else:
            # If HTMX request, return form with errors
            if request.headers.get('HX-Request'):
                return render(request, 'auth/register.html', {'form': form})
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'auth/register.html', {'form': form})

def notifications_dropdown_view(request):
    """View for rendering the notifications dropdown content."""
    if not request.user.is_authenticated:
        return HttpResponseForbidden()
    
    notifications = request.user.notifications.all()[:5]  # Get latest 5 notifications
    unread_count = request.user.notifications.filter(read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    
    return render(request, 'notifications/dropdown.html', context)

def settings_view(request):
    """View for user settings page."""
    if not request.user.is_authenticated:
        return redirect('login')
    
    context = {
        'user': request.user,
    }
    
    return render(request, 'core/settings.html', context)
