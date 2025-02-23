from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from source.apps.core.models import TimeStampedModel
from django.conf import settings


class Category(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True, verbose_name="Category Name")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Category Slug")
    description = models.TextField(blank=True, verbose_name="Category Description")

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


class Tag(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="Tag Name")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Tag Slug")

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Media(TimeStampedModel):
    MEDIA_TYPE_CHOICES = [
        ("image", "Image"),
        ("video", "Video"),
        ("document", "Document"),
    ]

    file = models.FileField(upload_to="media/%Y/%m/%d/", verbose_name="Media File")
    media_type = models.CharField(max_length=50, choices=MEDIA_TYPE_CHOICES, verbose_name="Media Type")
    alt_text = models.CharField(max_length=255, blank=True, verbose_name="Alt Text")

    class Meta:
        verbose_name = "Media"
        verbose_name_plural = "Media"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.media_type} - {self.file.name}"


class Article(TimeStampedModel):
    title = models.CharField(max_length=255, verbose_name="Title")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Slug")
    content = models.TextField(verbose_name="Content")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="article_author", verbose_name="Author"
    )
    categories = models.ManyToManyField(Category, related_name="article_categories", verbose_name="Categories")
    tags = models.ManyToManyField(Tag, related_name="article_tags", blank=True, verbose_name="Tags")
    media = models.ManyToManyField(Media, related_name="article_media", blank=True, verbose_name="Media Attachments")
    is_published = models.BooleanField(default=False, verbose_name="Is Published")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Published At")

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