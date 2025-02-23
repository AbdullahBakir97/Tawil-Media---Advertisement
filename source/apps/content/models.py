from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from source.apps.core.models import TimeStampedModel
from django.conf import settings
from .managers import CategoryManager, MediaManager, ArticleManager, MagazineManager
from taggit.managers import TaggableManager


class Category(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True, verbose_name="Category Name")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Category Slug")
    description = models.TextField(blank=True, verbose_name="Category Description")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    objects = CategoryManager()

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def get_related_articles(self):
        """Fetch all articles related to this category."""
        return self.article_categories.all()

    @classmethod
    def create_category(cls, name, description=''):
        category = cls(name=name, description=description)
        category.save()
        return category

    @classmethod
    def get_all_categories(cls):
        return cls.objects.all()

    @classmethod
    def update_category(cls, category_id, name=None, description=None):
        category = cls.objects.get(id=category_id)
        if name:
            category.name = name
        if description:
            category.description = description
        category.save()
        return category

    @classmethod
    def delete_category(cls, category_id):
        category = cls.objects.get(id=category_id)
        category.delete()


class Media(TimeStampedModel):
    MEDIA_TYPE_CHOICES = [
        ("image", "Image"),
        ("video", "Video"),
        ("document", "Document"),
    ]

    file = models.FileField(upload_to="media/%Y/%m/%d/", verbose_name="Media File")
    media_type = models.CharField(max_length=50, choices=MEDIA_TYPE_CHOICES, verbose_name="Media Type")
    alt_text = models.CharField(max_length=255, blank=True, verbose_name="Alt Text")

    objects = MediaManager()

    class Meta:
        verbose_name = "Media"
        verbose_name_plural = "Media"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.media_type} - {self.file.name}"

    @classmethod
    def upload_media(cls, file, media_type, alt_text=''):
        media = cls(file=file, media_type=media_type, alt_text=alt_text)
        media.save()
        return media

    @classmethod
    def get_all_media(cls):
        return cls.objects.all()


class Article(TimeStampedModel):
    title = models.CharField(max_length=255, verbose_name="Title")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Slug")
    content = models.TextField(verbose_name="Content")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="article_author", verbose_name="Author"
    )
    categories = models.ManyToManyField(Category, related_name="article_categories", verbose_name="Categories")
    tags = TaggableManager()
    media = models.ManyToManyField(Media, related_name="article_media", blank=True, verbose_name="Media Attachments")
    is_published = models.BooleanField(default=False, verbose_name="Is Published")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Published At")

    objects = ArticleManager()

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def publish(self):
        """Mark the article as published and set the published_at date."""
        self.is_published = True
        self.published_at = timezone.now()
        self.save()

    def unpublish(self):
        """Mark the article as unpublished."""
        self.is_published = False
        self.published_at = None
        self.save()

    def add_category(self, category):
        """Add a category to the article."""
        self.categories.add(category)

    def remove_category(self, category):
        """Remove a category from the article."""
        self.categories.remove(category)

    def add_tag(self, tag):
        """Add a tag to the article."""
        self.tags.add(tag)

    def remove_tag(self, tag):
        """Remove a tag from the article."""
        self.tags.remove(tag)

    @classmethod
    def create_article(cls, title, content, author, categories=None, tags=None):
        article = cls(title=title, content=content, author=author)
        article.save()
        if categories:
            article.categories.set(categories)
        if tags:
            article.tags.set(tags)
        return article

    @classmethod
    def get_all_articles(cls):
        return cls.objects.all()

    @classmethod
    def update_article(cls, article_id, title=None, content=None):
        article = cls.objects.get(id=article_id)
        if title:
            article.title = title
        if content:
            article.content = content
        article.save()
        return article

    @classmethod
    def delete_article(cls, article_id):
        article = cls.objects.get(id=article_id)
        article.delete()


class Magazine(TimeStampedModel):
    title = models.CharField(max_length=255, verbose_name="Magazine Title")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Magazine Slug")
    description = models.TextField(blank=True, verbose_name="Description")
    articles = models.ManyToManyField(Article, related_name="magazine_articles", verbose_name="Articles")
    cover_image = models.ForeignKey(
        Media, on_delete=models.SET_NULL, null=True, blank=True, related_name="magazine_covers", verbose_name="Cover Image"
    )
    is_published = models.BooleanField(default=False, verbose_name="Is Published")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Published At")

    objects = MagazineManager()

    class Meta:
        verbose_name = "Magazine"
        verbose_name_plural = "Magazines"
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def publish(self):
        """Mark the magazine as published and set the published_at date."""
        self.is_published = True
        self.published_at = timezone.now()
        self.save()

    def add_article(self, article):
        """Add an article to the magazine."""
        self.articles.add(article)

    def remove_article(self, article):
        """Remove an article from the magazine."""
        self.articles.remove(article)

    def get_all_articles(self):
        """Retrieve all articles associated with this magazine."""
        return self.articles.all()

    @classmethod
    def create_magazine(cls, title, description='', cover_image=None):
        magazine = cls(title=title, description=description, cover_image=cover_image)
        magazine.save()
        return magazine

    @classmethod
    def get_all_magazines(cls):
        return cls.objects.all()

    @classmethod
    def update_magazine(cls, magazine_id, title=None, description=None):
        magazine = cls.objects.get(id=magazine_id)
        if title:
            magazine.title = title
        if description:
            magazine.description = description
        magazine.save()
        return magazine

    @classmethod
    def delete_magazine(cls, magazine_id):
        magazine = cls.objects.get(id=magazine_id)
        magazine.delete()