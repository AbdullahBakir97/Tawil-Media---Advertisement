from django.urls import path

from .. import views

app_name = "magazines"

urlpatterns = [
    path("", views.MagazineListView.as_view(), name="list"),
    path("<slug:slug>/", views.MagazineDetailView.as_view(), name="detail"),
]
