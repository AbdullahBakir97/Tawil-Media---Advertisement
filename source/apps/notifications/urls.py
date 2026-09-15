from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.notification_list, name="list"),
    path("dropdown/", views.notifications_dropdown, name="notifications_dropdown"),
    path("mark-read/<int:notification_id>/", views.mark_as_read, name="mark_read"),
    path("mark-all-read/", views.mark_all_as_read, name="mark_all_read"),
    path("unread-count/", views.get_unread_count, name="unread_count"),
]
