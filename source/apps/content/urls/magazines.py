from django.urls import path

from source.apps.studio.views import ReaderView

from .. import views

app_name = "magazines"

urlpatterns = [
    path("", views.MagazineListView.as_view(), name="list"),
    path("<slug:slug>/read/", ReaderView.as_view(), name="read"),
    path("<slug:slug>/", views.MagazineDetailView.as_view(), name="detail"),
]
