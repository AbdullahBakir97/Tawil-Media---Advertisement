from django.contrib import admin

from .models import (
    FAQ,
    AdSlot,
    Announcement,
    HeroConfig,
    MagazinePage,
    Milestone,
    Partner,
    PressAsset,
    PressKit,
    Testimonial,
    Theme,
)


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ("name", "accent", "brand", "display_font", "is_default")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(HeroConfig)
class HeroConfigAdmin(admin.ModelAdmin):
    list_display = ("placement", "variant", "theme", "updated_at")
    fieldsets = (
        (None, {"fields": ("placement", "variant", "theme", "background")}),
        ("Blocks", {"fields": ("show_masthead", "show_stats", "show_ticker", "show_partners", "show_issue_facts")}),
        ("Copy · Deutsch", {"fields": ("kicker_de", "headline_de", "dek_de", "primary_label_de", "secondary_label_de")}),
        ("Copy · العربية", {"fields": ("kicker_ar", "headline_ar", "dek_ar", "primary_label_ar", "secondary_label_ar")}),
        ("Copy · English", {"fields": ("kicker_en", "headline_en", "dek_en", "primary_label_en", "secondary_label_en")}),
        ("Links and facts", {"fields": ("primary_url", "secondary_url", "pages_label", "price_label")}),
    )


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("text_de", "kind", "is_active", "starts_at", "ends_at", "order")
    list_editable = ("is_active", "order")
    list_filter = ("kind", "is_active")


@admin.register(AdSlot)
class AdSlotAdmin(admin.ModelAdmin):
    list_display = ("key", "format", "advertiser", "is_active", "starts_at", "ends_at", "weight")
    list_filter = ("format", "is_active")
    search_fields = ("key", "advertiser")


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "order")
    list_editable = ("is_active", "order")


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "is_active", "order")
    list_editable = ("is_active", "order")


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question_de", "page", "is_active", "order")
    list_editable = ("is_active", "order")
    list_filter = ("page",)


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ("year", "title_de", "is_active")


@admin.register(MagazinePage)
class MagazinePageAdmin(admin.ModelAdmin):
    list_display = ("magazine", "number", "width", "height")
    list_filter = ("magazine",)


class PressAssetInline(admin.TabularInline):
    model = PressAsset
    extra = 1
    fields = ("label", "kind", "background", "file", "preview", "credit", "order")


@admin.register(PressKit)
class PressKitAdmin(admin.ModelAdmin):
    list_display = ("name", "is_current", "contact_name", "contact_email", "updated_at")
    list_filter = ("is_current",)
    inlines = [PressAssetInline]
    fieldsets = (
        (None, {"fields": ("name", "is_current", "archive")}),
        ("Boilerplate", {
            "fields": ("boilerplate_de", "boilerplate_ar", "boilerplate_en"),
            "description": "The paragraph a journalist may quote. Keep it short and factual.",
        }),
        ("Press contact", {
            "fields": ("contact_name", "contact_role_de", "contact_role_ar", "contact_role_en",
                       "contact_email", "contact_phone"),
        }),
    )


@admin.register(PressAsset)
class PressAssetAdmin(admin.ModelAdmin):
    list_display = ("label", "kit", "kind", "background", "order")
    list_filter = ("kind", "background", "kit")
    list_editable = ("order",)
