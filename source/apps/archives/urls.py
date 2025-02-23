from django.urls import path
from . import views

app_name = 'archives'

urlpatterns = [
    path('test-chart/', views.test_chart_view, name='test_chart'),
    path('browse/', views.browse_view, name='browse'),
    path('api/search/', views.archive_search_api, name='search_api'),
    path('api/summary/', views.archive_summary_api, name='summary_api'),
]
