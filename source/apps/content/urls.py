from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    path('articles/', views.article_list, name='article_list'),
    path('articles/<slug:slug>/', views.article_detail, name='article_detail'),
    
    path('magazines/', views.magazine_list, name='magazine_list'),
    path('magazines/<slug:slug>/', views.magazine_detail, name='magazine_detail'),
]
