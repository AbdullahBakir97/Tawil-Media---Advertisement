from django.urls import path

from . import views

app_name = "advertising"

urlpatterns = [
    path("request/", views.request_campaign, name="request"),
]
