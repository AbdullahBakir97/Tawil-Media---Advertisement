from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "starts_at", "city", "kind", "status")
    list_filter = ("status", "kind", "is_online")
    list_editable = ("status",)
    search_fields = ("title", "title_de", "title_ar", "title_en", "venue", "city")
    date_hierarchy = "starts_at"
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("is_published", "published_at", "preview_token")
    fieldsets = (
        (None, {"fields": ("title", "slug", "kind", "image")}),
        ("Translations", {"fields": ("title_de", "title_ar", "title_en", "summary_de", "summary_ar", "summary_en")}),
        ("When and where", {"fields": ("starts_at", "ends_at", "venue", "address", "city", "is_online")}),
        ("Attending", {"fields": ("registration_url", "is_free", "price_note")}),
        ("Workflow", {"fields": ("status", "scheduled_for", "editor_note", "is_published", "published_at", "preview_token")}),
    )
