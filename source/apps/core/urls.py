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
]