from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import (
    ArchiveCategory,
    ArchiveYear,
    YearCategoryHighlight,
    Edition,
    EditionContent,
    ArchiveMetadata
)

@admin.register(ArchiveCategory)
class ArchiveCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'is_featured', 'display_order', 'show_icon')
    list_editable = ('is_featured', 'display_order')
    list_filter = ('is_featured',)
    search_fields = ('category__name', 'archive_description')
    ordering = ('display_order', 'category__name')
    
    def category_name(self, obj):
        return obj.category.name
    category_name.admin_order_field = 'category__name'
    
    def show_icon(self, obj):
        if obj.icon:
            return format_html('<img src="{}" width="50" height="50" />', obj.icon.file.url)
        return "No icon"
    show_icon.short_description = 'Icon'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'icon')

class YearCategoryHighlightInline(admin.TabularInline):
    model = YearCategoryHighlight
    extra = 1
    fields = ('category', 'highlight_description', 'display_order')
    ordering = ('display_order',)

@admin.register(ArchiveYear)
class ArchiveYearAdmin(admin.ModelAdmin):
    list_display = ('year', 'total_editions', 'is_active', 'show_cover')
    list_editable = ('is_active',)
    list_filter = ('is_active',)
    search_fields = ('year', 'description')
    inlines = [YearCategoryHighlightInline]
    
    def show_cover(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" width="100" height="100" />', obj.cover_image.file.url)
        return "No cover"
    show_cover.short_description = 'Cover Image'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cover_image')

class EditionContentInline(admin.StackedInline):
    model = EditionContent
    extra = 1
    fields = (
        ('title', 'content_type'),
        'categories',
        ('page_number', 'is_searchable'),
        'digital_content',
        'content_preview',
        'keywords'
    )
    filter_horizontal = ('categories',)
    raw_id_fields = ('original_article',)

@admin.register(Edition)
class EditionAdmin(admin.ModelAdmin):
    list_display = (
        'edition_title', 'archive_year_display', 'edition_number',
        'edition_type', 'publication_date', 'is_digitized'
    )
    list_filter = (
        'archive_year__year',
        'edition_type',
        'season',
        'is_digitized',
        'primary_category',
    )
    search_fields = ('title', 'description', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [EditionContentInline]
    raw_id_fields = ('cover_image', 'primary_category')
    date_hierarchy = 'publication_date'
    
    def edition_title(self, obj):
        return format_html(
            '<strong>{}</strong> <br/><small>Type: {}</small>',
            obj.title,
            obj.get_edition_type_display()
        )
    edition_title.short_description = 'Edition'
    
    def archive_year_display(self, obj):
        return f"{obj.archive_year.year}"
    archive_year_display.short_description = 'Year'
    archive_year_display.admin_order_field = 'archive_year__year'

    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('archive_year', 'edition_number'),
                ('title', 'slug'),
                'description',
            )
        }),
        ('Edition Details', {
            'fields': (
                ('edition_type', 'season'),
                'publication_date',
                ('primary_category', 'cover_image'),
            )
        }),
        ('Digitization', {
            'fields': (
                'is_digitized',
                ('page_count', 'file_size'),
            ),
            'classes': ('collapse',)
        }),
    )

class ArchiveMetadataInline(admin.StackedInline):
    model = ArchiveMetadata
    can_delete = False
    fields = (
        ('language', 'preservation_status'),
        'contributors',
        'source_info',
        ('digitization_date', 'digitization_notes'),
        'copyright_info',
        'tags'
    )

@admin.register(EditionContent)
class EditionContentAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'edition_info', 'content_type',
        'page_number', 'is_searchable'
    )
    list_filter = (
        'content_type',
        'is_searchable',
        'edition__archive_year__year',
        'categories',
    )
    search_fields = ('title', 'content_preview', 'keywords')
    filter_horizontal = ('categories',)
    raw_id_fields = ('edition', 'original_article')
    inlines = [ArchiveMetadataInline]
    
    def edition_info(self, obj):
        return format_html(
            '{} - Edition {}',
            obj.edition.archive_year.year,
            obj.edition.edition_number
        )
    edition_info.short_description = 'Edition'

    fieldsets = (
        ('Content Information', {
            'fields': (
                'edition',
                'title',
                ('content_type', 'page_number'),
                'categories',
            )
        }),
        ('Digital Content', {
            'fields': (
                'digital_content',
                'is_searchable',
                'original_article',
            )
        }),
        ('Content Details', {
            'fields': (
                'content_preview',
                'keywords',
            ),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'edition',
            'edition__archive_year'
        ).prefetch_related('categories')

# Register the YearCategoryHighlight model without customization
admin.site.register(YearCategoryHighlight)
