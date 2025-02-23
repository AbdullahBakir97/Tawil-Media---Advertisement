from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from source.apps.core.models import TimeStampedModel
from source.apps.content.models import Article, Magazine, Media, Category

class ArchiveCategory(TimeStampedModel):
    """Model to extend the base Category model with archive-specific attributes"""
    category = models.OneToOneField(
        Category,
        on_delete=models.CASCADE,
        related_name='archive_extension',
        verbose_name="Base Category"
    )
    is_featured = models.BooleanField(default=False, verbose_name="Is Featured in Archives")
    archive_description = models.TextField(blank=True, verbose_name="Archive-specific Description")
    icon = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='category_icons',
        verbose_name="Category Icon"
    )
    display_order = models.PositiveIntegerField(default=0, verbose_name="Display Order in Archives")

    class Meta:
        verbose_name = "Archive Category"
        verbose_name_plural = "Archive Categories"
        ordering = ['display_order', 'category__name']

    def __str__(self):
        return f"Archive: {self.category.name}"

    @classmethod
    def get_or_create_defaults(cls):
        """Create default archive categories if they don't exist"""
        default_categories = [
            ("historical", "Historical Content", True),
            ("editorial", "Editorial Content", True),
            ("interviews", "Interviews & Features", True),
            ("special_editions", "Special Editions", True),
            ("supplements", "Magazine Supplements", False),
            ("photo_galleries", "Photo Galleries", True),
            ("advertisements", "Historical Advertisements", False),
            ("cultural", "Cultural Content", True),
            ("news_archives", "News Archives", True),
        ]

        created_categories = []
        for name, desc, featured in default_categories:
            category, cat_created = Category.objects.get_or_create(
                name=name,
                defaults={'description': desc}
            )
            archive_cat, arch_created = cls.objects.get_or_create(
                category=category,
                defaults={
                    'is_featured': featured,
                    'archive_description': f"Archive collection of {desc.lower()}",
                    'display_order': len(created_categories) + 1
                }
            )
            created_categories.append(archive_cat)
        return created_categories

class ArchiveYear(TimeStampedModel):
    """Model to represent a year in the archive"""
    year = models.PositiveIntegerField(unique=True, verbose_name="Archive Year")
    description = models.TextField(blank=True, verbose_name="Year Description")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    total_editions = models.PositiveIntegerField(default=0, verbose_name="Total Editions")
    cover_image = models.ForeignKey(
        Media, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='year_covers',
        verbose_name="Year Cover Image"
    )
    featured_categories = models.ManyToManyField(
        Category,
        through='YearCategoryHighlight',
        related_name='featured_in_years',
        verbose_name="Featured Categories"
    )

    class Meta:
        verbose_name = "Archive Year"
        verbose_name_plural = "Archive Years"
        ordering = ['-year']

    def __str__(self):
        return f"Archive Year {self.year}"

    def update_total_editions(self):
        """Update the total number of editions for this year"""
        self.total_editions = self.editions.count()
        self.save()

    def get_category_content(self, category):
        """Get all content for a specific category in this year"""
        return EditionContent.objects.filter(
            edition__archive_year=self,
            categories=category
        ).order_by('edition__edition_number', 'page_number')

class YearCategoryHighlight(TimeStampedModel):
    """Model to manage category highlights for each archive year"""
    year = models.ForeignKey(
        ArchiveYear,
        on_delete=models.CASCADE,
        related_name='category_highlights',
        verbose_name="Archive Year"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='year_highlights',
        verbose_name="Category"
    )
    highlight_description = models.TextField(blank=True, verbose_name="Highlight Description")
    display_order = models.PositiveIntegerField(default=0, verbose_name="Display Order")
    featured_content = models.ManyToManyField(
        'EditionContent',
        related_name='category_features',
        blank=True,
        verbose_name="Featured Content"
    )

    class Meta:
        verbose_name = "Year Category Highlight"
        verbose_name_plural = "Year Category Highlights"
        ordering = ['year', 'display_order']
        unique_together = ['year', 'category']

    def __str__(self):
        return f"{self.year} - {self.category.name}"

class Edition(TimeStampedModel):
    """Model to represent a specific edition of the magazine"""
    EDITION_TYPES = [
        ('regular', 'Regular Edition'),
        ('special', 'Special Edition'),
        ('anniversary', 'Anniversary Edition'),
        ('supplement', 'Supplement'),
    ]

    SEASONS = [
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('fall', 'Fall'),
        ('winter', 'Winter'),
    ]

    archive_year = models.ForeignKey(
        ArchiveYear,
        on_delete=models.CASCADE,
        related_name='editions',
        verbose_name="Archive Year"
    )
    edition_number = models.PositiveIntegerField(verbose_name="Edition Number")
    title = models.CharField(max_length=255, verbose_name="Edition Title")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Edition Slug")
    description = models.TextField(blank=True, verbose_name="Edition Description")
    edition_type = models.CharField(
        max_length=20,
        choices=EDITION_TYPES,
        default='regular',
        verbose_name="Edition Type"
    )
    season = models.CharField(
        max_length=10,
        choices=SEASONS,
        blank=True,
        null=True,
        verbose_name="Season"
    )
    publication_date = models.DateField(verbose_name="Publication Date")
    cover_image = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        null=True,
        related_name='edition_covers',
        verbose_name="Edition Cover"
    )
    is_digitized = models.BooleanField(default=False, verbose_name="Is Digitized")
    page_count = models.PositiveIntegerField(default=0, verbose_name="Page Count")
    file_size = models.BigIntegerField(default=0, verbose_name="File Size in Bytes")
    primary_category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='primary_editions',
        verbose_name="Primary Category"
    )

    class Meta:
        verbose_name = "Edition"
        verbose_name_plural = "Editions"
        ordering = ['-archive_year__year', '-edition_number']
        unique_together = ['archive_year', 'edition_number']
        indexes = [
            models.Index(fields=['archive_year', 'edition_number']),
            models.Index(fields=['publication_date']),
            models.Index(fields=['edition_type']),
        ]

    def __str__(self):
        return f"{self.archive_year.year} - Edition {self.edition_number}: {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.archive_year.year}-{self.edition_number}-{self.title}")
        super().save(*args, **kwargs)
        self.archive_year.update_total_editions()

    def get_category_content(self, category):
        """Get all content in this edition for a specific category"""
        return self.contents.filter(categories=category).order_by('page_number')

class EditionContent(TimeStampedModel):
    """Model to store the actual content of an edition"""
    edition = models.ForeignKey(
        Edition,
        on_delete=models.CASCADE,
        related_name='contents',
        verbose_name="Edition"
    )
    title = models.CharField(max_length=255, verbose_name="Content Title")
    categories = models.ManyToManyField(
        Category,
        related_name='archived_content',
        verbose_name="Categories"
    )
    content_type = models.CharField(
        max_length=50,
        choices=[
            ('article', 'Article'),
            ('editorial', 'Editorial'),
            ('interview', 'Interview'),
            ('gallery', 'Photo Gallery'),
            ('advertisement', 'Advertisement'),
        ],
        verbose_name="Content Type"
    )
    page_number = models.PositiveIntegerField(verbose_name="Page Number")
    digital_content = models.FileField(
        upload_to='archives/edition_contents/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="Digital Content File"
    )
    is_searchable = models.BooleanField(default=False, verbose_name="Is Searchable")
    original_article = models.ForeignKey(
        Article,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='archived_versions',
        verbose_name="Original Article"
    )
    content_preview = models.TextField(blank=True, verbose_name="Content Preview")
    keywords = models.TextField(blank=True, verbose_name="Keywords")

    class Meta:
        verbose_name = "Edition Content"
        verbose_name_plural = "Edition Contents"
        ordering = ['edition', 'page_number']
        indexes = [
            models.Index(fields=['edition', 'page_number']),
            models.Index(fields=['content_type']),
        ]

    def __str__(self):
        return f"{self.edition} - {self.title} (Page {self.page_number})"

    def get_primary_category(self):
        """Get the primary category for this content"""
        return self.categories.first()

class ArchiveMetadata(TimeStampedModel):
    """Model to store additional metadata for archived content"""
    edition_content = models.OneToOneField(
        EditionContent,
        on_delete=models.CASCADE,
        related_name='metadata',
        verbose_name="Edition Content"
    )
    language = models.CharField(max_length=10, default='ar', verbose_name="Content Language")
    contributors = models.TextField(blank=True, verbose_name="Contributors")
    source_info = models.TextField(blank=True, verbose_name="Source Information")
    digitization_date = models.DateField(null=True, blank=True, verbose_name="Digitization Date")
    digitization_notes = models.TextField(blank=True, verbose_name="Digitization Notes")
    preservation_status = models.CharField(
        max_length=20,
        choices=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
        ],
        default='good',
        verbose_name="Preservation Status"
    )
    copyright_info = models.TextField(blank=True, verbose_name="Copyright Information")
    tags = models.TextField(blank=True, verbose_name="Content Tags")

    class Meta:
        verbose_name = "Archive Metadata"
        verbose_name_plural = "Archive Metadata"

    def __str__(self):
        return f"Metadata for {self.edition_content}"
