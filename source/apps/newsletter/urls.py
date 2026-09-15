from django.urls import path

from . import views

app_name = "newsletter"

urlpatterns = [
    path("subscribe/", views.subscribe, name="subscribe"),
    path("unsubscribe/", views.unsubscribe_info, name="unsubscribe_info"),
    path("unsubscribe/<uuid:token>/", views.unsubscribe, name="unsubscribe"),
]
