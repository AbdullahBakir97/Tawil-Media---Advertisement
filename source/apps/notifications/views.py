from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .models import Notification


def _context(user, limit=None):
    queryset = Notification.objects.for_user(user)
    return {
        "notifications": queryset[:limit] if limit else queryset,
        "unread_count": queryset.unread().count(),
    }


@login_required
def notification_list(request):
    return render(request, "notifications/list.html", _context(request.user))


@login_required
def notifications_dropdown(request):
    """HTMX partial for the header bell."""
    return render(request, "notifications/dropdown.html", _context(request.user, limit=5))


@login_required
@require_POST
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.mark_as_read()
    if request.headers.get("HX-Request"):
        return render(request, "notifications/dropdown.html", _context(request.user, limit=5))
    return JsonResponse({"status": "success"})


@login_required
@require_POST
def mark_all_as_read(request):
    Notification.objects.for_user(request.user).unread().update(read=True)
    if request.headers.get("HX-Request"):
        return render(request, "notifications/dropdown.html", _context(request.user, limit=5))
    return JsonResponse({"status": "success"})


@login_required
def get_unread_count(request):
    return JsonResponse({"unread_count": Notification.objects.for_user(request.user).unread().count()})
