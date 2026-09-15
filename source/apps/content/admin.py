from django.contrib import admin

from .models import Article, Category, Contributor, Magazine, Media


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}  # Automatically populate slug from name
    list_display = ('name', 'slug', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description', 'is_active', 'order', 'accent')}),
        ('Translations', {'fields': ('name_de', 'name_ar', 'name_en', 'intro_de', 'intro_ar', 'intro_en')}),
    )


@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
    list_display = ('name', 'role_de', 'user', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'role_de', 'role_ar', 'role_en', 'user__email')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'user', 'portrait', 'is_active', 'order')}),
        ('Role', {'fields': ('role_de', 'role_ar', 'role_en')}),
        ('Biography', {'fields': ('bio_de', 'bio_ar', 'bio_en')}),
        ('Contact', {'fields': ('email', 'website', 'social_handle', 'social_url')}),
    )

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
