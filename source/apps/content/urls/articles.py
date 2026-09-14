from django.urls import path

from .. import views

app_name = "articles"

urlpatterns = [
    path("", views.ArticleListView.as_view(), name="list"),
    path("category/<slug:slug>/", views.ArticleListView.as_view(), name="by_category"),
    path("tag/<slug:tag>/", views.ArticleListView.as_view(), name="by_tag"),
    path("<slug:slug>/", views.ArticleDetailView.as_view(), name="detail"),
]
