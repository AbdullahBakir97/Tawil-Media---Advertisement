from django.urls import path

from . import views

app_name = "studio"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("hero/", views.HeroEditorView.as_view(), name="hero"),
    path("hero/preview/<slug:variant>/", views.HeroPreviewView.as_view(), name="hero_preview"),
    path("themes/", views.ThemeListView.as_view(), name="themes"),
    path("themes/new/", views.ThemeEditView.as_view(), name="theme_new"),
    path("themes/<int:pk>/", views.ThemeEditView.as_view(), name="theme_edit"),
    path("announcements/", views.AnnouncementListView.as_view(), name="announcements"),
    path("media/", views.MediaLibraryView.as_view(), name="media"),
    path("magazines/<slug:slug>/render/", views.MagazinePagesView.as_view(), name="magazine_render"),
]
