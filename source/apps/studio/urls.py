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
    path("ad-slots/", views.AdSlotListView.as_view(), name="ad_slots"),
    path("partners/", views.PartnerListView.as_view(), name="partners"),
    path("voices/", views.TestimonialListView.as_view(), name="testimonials"),
    path("faq/", views.FAQListView.as_view(), name="faq"),
    path("timeline/", views.MilestoneListView.as_view(), name="timeline"),
    path("editions/", views.MagazineEditorView.as_view(), name="magazines"),
    path("editions/<int:pk>/", views.MagazineEditorView.as_view(), name="magazine_edit"),
    path("media/", views.MediaLibraryView.as_view(), name="media"),
    path("desk/", views.DeskView.as_view(), name="desk"),
    path("articles/new/", views.ArticleEditorView.as_view(), name="article_new"),
    path("articles/<int:pk>/", views.ArticleEditorView.as_view(), name="article_edit"),
    path("newsletter/", views.NewsletterListView.as_view(), name="newsletter"),
    path("newsletter/<int:pk>/", views.NewsletterEditView.as_view(), name="newsletter_edit"),
    path("newsletter/<int:pk>/preview/", views.NewsletterPreviewView.as_view(), name="newsletter_preview"),
    path("magazines/<slug:slug>/render/", views.MagazinePagesView.as_view(), name="magazine_render"),
]
