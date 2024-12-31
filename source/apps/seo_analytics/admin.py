from django.contrib import admin
from .models import SEOSettings, SEOPageMeta, AnalyticsEvent, PageVisit, SearchRanking

@admin.register(SEOSettings)
class SEOSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_title', 'site_description', 'robots_txt', 'sitemap_url', 'canonical_url')
    search_fields = ('site_title',)
    ordering = ('site_title',)

@admin.register(SEOPageMeta)
class SEOPageMetaAdmin(admin.ModelAdmin):
    list_display = ('url', 'meta_title', 'meta_description', 'no_index', 'no_follow')
    search_fields = ('url', 'meta_title')
    list_filter = ('no_index', 'no_follow')
    ordering = ('url',)

@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'user', 'url', 'occurred_at')
    search_fields = ('event_name', 'user__email', 'url')
    list_filter = ('user',)
    ordering = ('-occurred_at',)

@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'url', 'visit_date')
    search_fields = ('url', 'user__email', 'ip_address')
    list_filter = ('user',)
    ordering = ('-visit_date',)

@admin.register(SearchRanking)
class SearchRankingAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'url', 'ranking', 'search_engine', 'checked_at')
    search_fields = ('keyword', 'url')
    list_filter = ('search_engine',)
    ordering = ('-checked_at',)
