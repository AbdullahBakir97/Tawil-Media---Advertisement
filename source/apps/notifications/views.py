from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from .models import Notification

@login_required
def notification_list(request):
    # Get notifications from Redis (with database fallback)
    notifications = Notification.get_recent_notifications(request.user, limit=10)
    unread_count = sum(1 for n in notifications if not n['read'])
    
    return render(request, 'notifications/list.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })

@login_required
def notifications_dropdown(request):
    """View for rendering the notifications dropdown content."""
    notifications = Notification.get_recent_notifications(request.user, limit=5)
    unread_count = sum(1 for n in notifications if not n['read'])
    
    return render(request, 'notifications/dropdown.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })

@login_required
def mark_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, recipient=request.user)
        notification.mark_as_read()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notification not found'}, status=404)

@login_required
def get_unread_count(request):
    """Get unread notifications count for real-time updates."""
    notifications = Notification.get_recent_notifications(request.user)
    unread_count = sum(1 for n in notifications if not n['read'])
    return JsonResponse({'unread_count': unread_count})
