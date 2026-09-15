from django.contrib import admin

from .models import (
    AdCampaign,
    AdPerformance,
    AdPlacement,
    Advertisement,
    Advertiser,
    CampaignRequest,
    CampaignRequestItem,
    MediaKit,
    RateCard,
)


@admin.register(Advertiser)
class AdvertiserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')
    search_fields = ('name', 'email')
    list_filter = ()
    ordering = ('name',)

@admin.register(AdCampaign)
class AdCampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'advertiser', 'budget', 'start_date', 'end_date', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active', 'advertiser')
    ordering = ('-start_date',)

@admin.register(AdPlacement)
class AdPlacementAdmin(admin.ModelAdmin):
    list_display = ('name', 'page', 'position', 'is_active')
    search_fields = ('name', 'page')
    list_filter = ('is_active',)
    ordering = ('page', 'position')

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('name', 'campaign', 'placement', 'url', 'impressions', 'clicks', 'is_active')
    search_fields = ('name', 'url')
    list_filter = ('is_active', 'campaign', 'placement')
    ordering = ('-start_date',)

@admin.register(AdPerformance)
class AdPerformanceAdmin(admin.ModelAdmin):
    list_display = ('advertisement', 'total_impressions', 'total_clicks', 'click_through_rate')
    search_fields = ('advertisement__name',)
    ordering = ('advertisement',)


@admin.register(RateCard)
class RateCardAdmin(admin.ModelAdmin):
    list_display = ("name_de", "channel", "price", "unit", "size_label", "is_featured", "is_active", "order")
    list_editable = ("price", "is_featured", "is_active", "order")
    list_filter = ("channel", "is_active", "is_featured")
    prepopulated_fields = {"slug": ("name_de",)}
    fieldsets = (
        (None, {"fields": ("channel", "slug", "price", "unit", "is_featured", "is_active", "order")}),
        ("Specification", {"fields": ("specs", "width", "height")}),
        ("Deutsch", {"fields": ("name_de", "description_de")}),
        ("العربية", {"fields": ("name_ar", "description_ar")}),
        ("English", {"fields": ("name_en", "description_en")}),
    )


@admin.register(MediaKit)
class MediaKitAdmin(admin.ModelAdmin):
    list_display = ("title", "year", "is_active", "updated_at")


class CampaignRequestItemInline(admin.TabularInline):
    model = CampaignRequestItem
    extra = 0
    readonly_fields = ("rate_card", "quantity", "unit_price")
    can_delete = False


@admin.register(CampaignRequest)
class CampaignRequestAdmin(admin.ModelAdmin):
    list_display = ("company", "contact_name", "email", "estimate", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("company", "contact_name", "email")
    readonly_fields = ("company", "contact_name", "email", "phone", "message", "estimate", "language", "editions")
    inlines = [CampaignRequestItemInline]
    list_editable = ("status",)
