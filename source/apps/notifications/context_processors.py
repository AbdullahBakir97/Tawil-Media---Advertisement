def notifications(request):
    """Unread badge count for the header, without a query for anonymous users."""
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return {"unread_notifications_count": 0}
    return {"unread_notifications_count": user.notifications.filter(read=False).count()}
