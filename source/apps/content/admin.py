from django.contrib import admin
from .models import Category, Media, Article, Magazine

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_active',)

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('media_type', 'file', 'alt_text', 'created_at')
    list_filter = ('media_type', 'created_at')
    search_fields = ('alt_text', 'file')
    date_hierarchy = 'created_at'

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'published_at')
    search_fields = ('title', 'content', 'author__email')
    list_filter = ('is_published', 'categories', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('categories', 'media')
    date_hierarchy = 'published_at'
    ordering = ('-published_at', '-created_at')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'content')
        }),
        ('Publishing', {
            'fields': ('author', 'is_published', 'published_at')
        }),
        ('Categorization', {
            'fields': ('categories', 'tags')
        }),
        ('Media', {
            'fields': ('media',)
        }),
    )

@admin.register(Magazine)
class MagazineAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'published_at', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('is_published', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('articles',)
    date_hierarchy = 'published_at'
    ordering = ('-published_at', '-created_at')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description')
        }),
        ('Publishing', {
            'fields': ('is_published', 'published_at')
        }),
        ('Content', {
            'fields': ('cover_image', 'articles')
        }),
    )
