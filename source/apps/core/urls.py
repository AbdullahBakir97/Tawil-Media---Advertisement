from django.urls import path, include
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('advertise/', views.advertise_view, name='advertise'),
    path('search/', views.search_view, name='search'),
    path('search/suggestions/', views.search_suggestions_view, name='search_suggestions'),
    path('terms/', views.terms_view, name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('register/', views.register, name='register'),
    path('help/', views.help_view, name='help'),
    path('careers/', views.careers_view, name='careers'),
    path('cookies/', views.cookies_view, name='cookies'),
    path('sitemap/', views.sitemap_view, name='sitemap'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('tailwind-test/', views.tailwind_test_view, name='tailwind_test'),
    path('design-system/', views.premium_design_system_view, name='premium_design_system'),
    path('style-guide/', views.style_guide_view, name='style_guide'),
    path('style-guide/components/', views.style_guide_components_view, name='style_guide_components'),
    path('style-guide/layouts/', views.style_guide_layouts_view, name='style_guide_layouts'),
    path('style-guide/pages/', views.style_guide_pages_view, name='style_guide_pages'),
    path('examples/dashboard/', views.dashboard_example_view, name='dashboard_example'),
    path('examples/magazine-browse/', views.magazine_browse_example_view, name='magazine_browse_example'),
    path('examples/archive-browse/', views.archive_browse_example_view, name='archive_browse_example'),
    path('design-system/index/', views.design_system_index_view, name='design_system_index'),
]