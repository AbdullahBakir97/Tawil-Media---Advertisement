from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import PasswordResetRequest, User, UserActivity, UserProfile, UserRole


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    extra = 0


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Auth-aware admin so passwords are hashed and the change-password form works."""

    ordering = ("email",)
    list_display = ("email", "username", "first_name", "last_name", "is_staff", "is_verified", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active", "is_verified")
    search_fields = ("email", "username", "first_name", "last_name")
    inlines = (UserProfileInline,)
    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "phone_number", "date_of_birth", "profile_picture")}),
        (_("Status"), {"fields": ("is_verified", "last_login_ip")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "first_name", "last_name", "password1", "password2"),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "country")
    search_fields = ("user__email", "city", "country")


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    filter_horizontal = ("permissions",)


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ("user", "activity_type", "activity_date", "ip_address")
    list_filter = ("activity_type",)
    search_fields = ("user__email", "activity_type")
    date_hierarchy = "activity_date"


@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "request_date", "expiry_date", "is_used")
    list_filter = ("is_used",)
    search_fields = ("user__email",)
