from django.contrib import admin
from .models import User, UserProfile, UserRole, UserActivity, PasswordResetRequest

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_verified')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_verified')
    ordering = ('email',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'city', 'country', 'zip_code', 'gender')
    search_fields = ('user__email', 'address', 'city')
    list_filter = ('gender',)
    ordering = ('user',)

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'activity_date', 'ip_address')
    search_fields = ('user__email', 'activity_type')
    list_filter = ('activity_type',)
    ordering = ('-activity_date',)

@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'request_date', 'expiry_date', 'is_used')
    search_fields = ('user__email', 'token')
    list_filter = ('is_used',)
    ordering = ('-request_date',)
