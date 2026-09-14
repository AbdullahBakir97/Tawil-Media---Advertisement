from django.urls import include, path

from . import views

notification_patterns = (
    [
        path("", views.NotificationListView.as_view(), name="list"),
    ],
    "notifications",
)

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("password/reset/", views.PasswordResetView.as_view(), name="password_reset"),
    path(
        "password/reset/<uidb64>/<token>/",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("password/change/", views.PasswordChangeView.as_view(), name="password_change"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("settings/", views.SettingsView.as_view(), name="settings"),
    path("settings/", views.SettingsView.as_view(), name="profile_settings"),
    path("settings/profile/", views.UpdateProfileView.as_view(), name="update_profile"),
    path("settings/security/", views.UpdateSecurityView.as_view(), name="update_security"),
    path("settings/notifications/", views.UpdateNotificationsView.as_view(), name="update_notifications"),
    path("notifications/", include(notification_patterns)),
]
