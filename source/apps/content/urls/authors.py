from django.urls import path

from .. import views

app_name = "authors"

urlpatterns = [
    path("", views.ContributorListView.as_view(), name="list"),
    path("<slug:slug>/", views.ContributorDetailView.as_view(), name="detail"),
]
