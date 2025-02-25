from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication views
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='users:login'), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # Password reset
    path('password/reset/', views.password_reset_view, name='password_reset'),
    path('password/reset/<str:token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    
    # User dashboard and profile
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('settings/', views.settings_view, name='settings'),
    path('profile/', views.profile_view, name='profile'),
    
    # Settings update endpoints
    path('settings/update-profile/', views.update_profile_view, name='update_profile'),
    path('settings/update-security/', views.update_security_view, name='update_security'),
    path('settings/update-notifications/', views.update_notifications_view, name='update_notifications'),
    path('settings/terminate-session/', views.terminate_session_view, name='terminate_session'),
]
