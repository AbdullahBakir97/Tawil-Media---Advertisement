from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import Truncator, slugify
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager

from source.apps.core.models import TimeStampedModel

from .imaging import measure
from .managers import ArticleManager, CategoryManager, MagazineManager, MediaManager


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
        ("image", _("Image")),
        ("video", _("Video")),
        ("document", _("Document")),
    ]

    file = models.FileField(upload_to="media/%Y/%m/%d/", verbose_name="Media File")
    media_type = models.CharField(max_length=50, choices=MEDIA_TYPE_CHOICES, verbose_name="Media Type")
    alt_text = models.CharField(max_length=255, blank=True, verbose_name="Alt Text")
    caption = models.CharField(max_length=255, blank=True, verbose_name="Caption")
    credit = models.CharField(max_length=160, blank=True, verbose_name="Credit")
    width = models.PositiveIntegerField(null=True, blank=True, editable=False)
    height = models.PositiveIntegerField(null=True, blank=True, editable=False)
    focal_x = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Focal point across",
        help_text="0 is the left edge, 1 the right. Crops keep this point in view.",
    )
    focal_y = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Focal point down",
        help_text="0 is the top edge, 1 the bottom.",
    )

    objects = MediaManager()

    class Meta:
        verbose_name = "Media"
        verbose_name_plural = "Media"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.media_type} - {self.file.name}"

    def save(self, *args, **kwargs):
        """Remember the pixel size so templates can reserve the space before the
        image loads. A file we cannot open (a PDF, a broken upload) simply keeps
        no dimensions; nothing else depends on them."""
        super().save(*args, **kwargs)
        if self.media_type == "image" and (self.width is None or self.height is None):
            size = measure(self.file)
            if size:
                type(self).objects.filter(pk=self.pk).update(width=size[0], height=size[1])
                self.width, self.height = size

    @property
    def is_image(self):
        return self.media_type == "image"

    @property
    def aspect_ratio(self):
        """CSS ratio for the box the image will fill, or None when unknown."""
        return f"{self.width} / {self.height}" if self.width and self.height else None

    @property
    def object_position(self):
        """The focal point as a CSS object-position, so a crop keeps the subject."""
        return f"{round(self.focal_x * 100)}% {round(self.focal_y * 100)}%"

    @property
    def label(self):
        return self.alt_text or self.caption or self.file.name.rsplit("/", 1)[-1]

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
    tags = TaggableManager(blank=True)
    media = models.ManyToManyField(Media, related_name="article_media", blank=True, verbose_name="Media Attachments")
    is_published = models.BooleanField(default=False, verbose_name="Is Published")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Published At")
    is_sponsored = models.BooleanField(default=False, verbose_name="Sponsored content")
    sponsor_name = models.CharField(max_length=120, blank=True, verbose_name="Sponsor")

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

    def get_absolute_url(self):
        return reverse("articles:detail", args=[self.slug])

    @property
    def cover(self):
        """First attached image, used as the card and hero picture."""
        for item in self.media.all():
            if item.media_type == "image":
                return item
        return None

    @property
    def excerpt(self):
        return Truncator(strip_tags(self.content)).words(32, truncate=" …")

    @property
    def reading_time(self):
        """Minutes at ~200 words per minute, never below 1."""
        words = len(strip_tags(self.content).split())
        return max(1, round(words / 200))

    @property
    def primary_category(self):
        return self.categories.first()

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
    pdf = models.FileField(upload_to="magazines/pdf/", blank=True, verbose_name="Edition PDF")
    pdf_rendered = models.CharField(max_length=255, blank=True, editable=False, verbose_name="Rendered PDF")
    issue_number = models.PositiveIntegerField(null=True, blank=True, verbose_name="Issue number")
    theme = models.ForeignKey(
        "studio.Theme", on_delete=models.SET_NULL, null=True, blank=True, related_name="magazines", verbose_name="Theme"
    )

    objects = MagazineManager()

    class Meta:
        verbose_name = "Magazine"
        verbose_name_plural = "Magazines"
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("magazines:detail", args=[self.slug])

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
