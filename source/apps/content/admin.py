from django.contrib import admin

from .models import Article, Category, Magazine, Media


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}  # Automatically populate slug from name

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('media_type', 'file', 'alt_text', 'credit', 'created_at')
    list_filter = ('media_type',)
    search_fields = ('alt_text', 'caption', 'credit', 'file')
    readonly_fields = ('width', 'height')
    fieldsets = (
        (None, {'fields': ('file', 'media_type', ('width', 'height'))}),
        ('Description', {'fields': ('alt_text', 'caption', 'credit')}),
        ('Focal point', {
            'fields': ('focal_x', 'focal_y'),
            'description': 'Easier to set in the Studio media library, where you click the picture itself.',
        }),
    )

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'scheduled_for', 'published_at')
    search_fields = ('title', 'author__email')
    list_filter = ('status', 'categories')
    list_editable = ('status',)
    ordering = ('-published_at',)
    readonly_fields = ('is_published', 'published_at', 'preview_token')
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'content', 'author')}),
        ('Filing', {'fields': ('categories', 'tags', 'media', 'is_sponsored', 'sponsor_name')}),
        ('Workflow', {
            'fields': ('status', 'scheduled_for', 'editor_note', 'is_published', 'published_at', 'preview_token'),
            'description': 'The status decides whether the article is live; is_published follows it.',
        }),
    )

@admin.register(Magazine)
class MagazineAdmin(admin.ModelAdmin):
    list_display = ('title', 'issue_number', 'status', 'scheduled_for', 'published_at')
    search_fields = ('title',)
    list_filter = ('status',)
    list_editable = ('status',)
    ordering = ('-published_at',)
    readonly_fields = ('is_published', 'published_at', 'preview_token')
