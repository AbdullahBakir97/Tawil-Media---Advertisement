from django.contrib import admin
from .models import Category, Tag, Media, Article, Magazine

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}  # Automatically populate slug from name

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}  # Automatically populate slug from name

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('media_type', 'file', 'alt_text')
    list_filter = ('media_type',)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'published_at')
    search_fields = ('title', 'author__email')
    list_filter = ('is_published', 'categories')
    ordering = ('-published_at',)

@admin.register(Magazine)
class MagazineAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'published_at')
    search_fields = ('title',)
    list_filter = ('is_published',)
    ordering = ('-published_at',)
