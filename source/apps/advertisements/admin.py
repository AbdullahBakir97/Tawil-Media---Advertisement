from django.contrib import admin
from .models import Advertiser, AdCampaign, AdPlacement, Advertisement, AdPerformance

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
