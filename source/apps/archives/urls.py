from django.urls import path

from . import views

app_name = "archives"

urlpatterns = [
    path("", views.ArchiveBrowseView.as_view(), name="browse"),
    path("<int:year>/", views.ArchiveYearView.as_view(), name="year"),
    path("edition/<slug:slug>/", views.EditionDetailView.as_view(), name="edition"),
]
