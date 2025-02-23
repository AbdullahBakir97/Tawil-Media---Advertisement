from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from .models import NewsletterSubscriber

# Create your views here.

@require_http_methods(["POST"])
@csrf_protect
def subscribe(request):
    email = request.POST.get('email')
    
    if not email:
        return JsonResponse({
            'status': 'error',
            'message': 'Email is required'
        }, status=400)
    
    try:
        subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
        
        if created:
            return JsonResponse({
                'status': 'success',
                'message': 'Successfully subscribed to newsletter!'
            })
        else:
            return JsonResponse({
                'status': 'info',
                'message': 'You are already subscribed to our newsletter.'
            })
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred. Please try again later.'
        }, status=500)
