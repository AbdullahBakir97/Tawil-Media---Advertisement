# Generated by Django 5.1.4 on 2025-02-23 14:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('content', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArchiveCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('is_featured', models.BooleanField(default=False, verbose_name='Is Featured in Archives')),
                ('archive_description', models.TextField(blank=True, verbose_name='Archive-specific Description')),
                ('display_order', models.PositiveIntegerField(default=0, verbose_name='Display Order in Archives')),
                ('category', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='archive_extension', to='content.category', verbose_name='Base Category')),
                ('icon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='category_icons', to='content.media', verbose_name='Category Icon')),
            ],
            options={
                'verbose_name': 'Archive Category',
                'verbose_name_plural': 'Archive Categories',
                'ordering': ['display_order', 'category__name'],
            },
        ),
        migrations.CreateModel(
            name='ArchiveYear',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('year', models.PositiveIntegerField(unique=True, verbose_name='Archive Year')),
                ('description', models.TextField(blank=True, verbose_name='Year Description')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('total_editions', models.PositiveIntegerField(default=0, verbose_name='Total Editions')),
                ('cover_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='year_covers', to='content.media', verbose_name='Year Cover Image')),
            ],
            options={
                'verbose_name': 'Archive Year',
                'verbose_name_plural': 'Archive Years',
                'ordering': ['-year'],
            },
        ),
        migrations.CreateModel(
            name='Edition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('edition_number', models.PositiveIntegerField(verbose_name='Edition Number')),
                ('title', models.CharField(max_length=255, verbose_name='Edition Title')),
                ('slug', models.SlugField(max_length=255, unique=True, verbose_name='Edition Slug')),
                ('description', models.TextField(blank=True, verbose_name='Edition Description')),
                ('edition_type', models.CharField(choices=[('regular', 'Regular Edition'), ('special', 'Special Edition'), ('anniversary', 'Anniversary Edition'), ('supplement', 'Supplement')], default='regular', max_length=20, verbose_name='Edition Type')),
                ('season', models.CharField(blank=True, choices=[('spring', 'Spring'), ('summer', 'Summer'), ('fall', 'Fall'), ('winter', 'Winter')], max_length=10, null=True, verbose_name='Season')),
                ('publication_date', models.DateField(verbose_name='Publication Date')),
                ('is_digitized', models.BooleanField(default=False, verbose_name='Is Digitized')),
                ('page_count', models.PositiveIntegerField(default=0, verbose_name='Page Count')),
                ('file_size', models.BigIntegerField(default=0, verbose_name='File Size in Bytes')),
                ('archive_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='editions', to='archives.archiveyear', verbose_name='Archive Year')),
                ('cover_image', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='edition_covers', to='content.media', verbose_name='Edition Cover')),
                ('primary_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_editions', to='content.category', verbose_name='Primary Category')),
            ],
            options={
                'verbose_name': 'Edition',
                'verbose_name_plural': 'Editions',
                'ordering': ['-archive_year__year', '-edition_number'],
            },
        ),
        migrations.CreateModel(
            name='EditionContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('title', models.CharField(max_length=255, verbose_name='Content Title')),
                ('content_type', models.CharField(choices=[('article', 'Article'), ('editorial', 'Editorial'), ('interview', 'Interview'), ('gallery', 'Photo Gallery'), ('advertisement', 'Advertisement')], max_length=50, verbose_name='Content Type')),
                ('page_number', models.PositiveIntegerField(verbose_name='Page Number')),
                ('digital_content', models.FileField(blank=True, null=True, upload_to='archives/edition_contents/%Y/%m/', verbose_name='Digital Content File')),
                ('is_searchable', models.BooleanField(default=False, verbose_name='Is Searchable')),
                ('content_preview', models.TextField(blank=True, verbose_name='Content Preview')),
                ('keywords', models.TextField(blank=True, verbose_name='Keywords')),
                ('categories', models.ManyToManyField(related_name='archived_content', to='content.category', verbose_name='Categories')),
                ('edition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contents', to='archives.edition', verbose_name='Edition')),
                ('original_article', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='archived_versions', to='content.article', verbose_name='Original Article')),
            ],
            options={
                'verbose_name': 'Edition Content',
                'verbose_name_plural': 'Edition Contents',
                'ordering': ['edition', 'page_number'],
            },
        ),
        migrations.CreateModel(
            name='ArchiveMetadata',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('language', models.CharField(default='ar', max_length=10, verbose_name='Content Language')),
                ('contributors', models.TextField(blank=True, verbose_name='Contributors')),
                ('source_info', models.TextField(blank=True, verbose_name='Source Information')),
                ('digitization_date', models.DateField(blank=True, null=True, verbose_name='Digitization Date')),
                ('digitization_notes', models.TextField(blank=True, verbose_name='Digitization Notes')),
                ('preservation_status', models.CharField(choices=[('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor')], default='good', max_length=20, verbose_name='Preservation Status')),
                ('copyright_info', models.TextField(blank=True, verbose_name='Copyright Information')),
                ('tags', models.TextField(blank=True, verbose_name='Content Tags')),
                ('edition_content', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='metadata', to='archives.editioncontent', verbose_name='Edition Content')),
            ],
            options={
                'verbose_name': 'Archive Metadata',
                'verbose_name_plural': 'Archive Metadata',
            },
        ),
        migrations.CreateModel(
            name='YearCategoryHighlight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('highlight_description', models.TextField(blank=True, verbose_name='Highlight Description')),
                ('display_order', models.PositiveIntegerField(default=0, verbose_name='Display Order')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='year_highlights', to='content.category', verbose_name='Category')),
                ('featured_content', models.ManyToManyField(blank=True, related_name='category_features', to='archives.editioncontent', verbose_name='Featured Content')),
                ('year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category_highlights', to='archives.archiveyear', verbose_name='Archive Year')),
            ],
            options={
                'verbose_name': 'Year Category Highlight',
                'verbose_name_plural': 'Year Category Highlights',
                'ordering': ['year', 'display_order'],
            },
        ),
        migrations.AddField(
            model_name='archiveyear',
            name='featured_categories',
            field=models.ManyToManyField(related_name='featured_in_years', through='archives.YearCategoryHighlight', to='content.category', verbose_name='Featured Categories'),
        ),
        migrations.AddIndex(
            model_name='edition',
            index=models.Index(fields=['archive_year', 'edition_number'], name='archives_ed_archive_94b841_idx'),
        ),
        migrations.AddIndex(
            model_name='edition',
            index=models.Index(fields=['publication_date'], name='archives_ed_publica_197877_idx'),
        ),
        migrations.AddIndex(
            model_name='edition',
            index=models.Index(fields=['edition_type'], name='archives_ed_edition_5856f7_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='edition',
            unique_together={('archive_year', 'edition_number')},
        ),
        migrations.AddIndex(
            model_name='editioncontent',
            index=models.Index(fields=['edition', 'page_number'], name='archives_ed_edition_7bd60b_idx'),
        ),
        migrations.AddIndex(
            model_name='editioncontent',
            index=models.Index(fields=['content_type'], name='archives_ed_content_8854be_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='yearcategoryhighlight',
            unique_together={('year', 'category')},
        ),
    ]
