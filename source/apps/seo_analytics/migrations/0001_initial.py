# Generated by Django 5.1.4 on 2024-12-31 23:26

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AnalyticsEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created At"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated At"),
                ),
                (
                    "event_name",
                    models.CharField(max_length=100, verbose_name="Event Name"),
                ),
                ("url", models.URLField(verbose_name="Event URL")),
                (
                    "event_data",
                    models.JSONField(blank=True, null=True, verbose_name="Event Data"),
                ),
                (
                    "occurred_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Occurred At"),
                ),
            ],
            options={
                "verbose_name": "Analytics Event",
                "verbose_name_plural": "Analytics Events",
                "ordering": ["-occurred_at"],
            },
        ),
        migrations.CreateModel(
            name="PageVisit",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created At"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated At"),
                ),
                ("ip_address", models.GenericIPAddressField(verbose_name="IP Address")),
                ("url", models.URLField(verbose_name="Visited URL")),
                (
                    "referrer",
                    models.URLField(blank=True, null=True, verbose_name="Referrer"),
                ),
                ("user_agent", models.TextField(blank=True, verbose_name="User Agent")),
                (
                    "visit_date",
                    models.DateTimeField(auto_now_add=True, verbose_name="Visit Date"),
                ),
            ],
            options={
                "verbose_name": "Page Visit",
                "verbose_name_plural": "Page Visits",
                "ordering": ["-visit_date"],
            },
        ),
        migrations.CreateModel(
            name="SearchRanking",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created At"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated At"),
                ),
                ("keyword", models.CharField(max_length=100, verbose_name="Keyword")),
                ("url", models.URLField(verbose_name="Page URL")),
                (
                    "ranking",
                    models.PositiveIntegerField(verbose_name="Search Engine Ranking"),
                ),
                (
                    "search_engine",
                    models.CharField(
                        choices=[
                            ("google", "Google"),
                            ("bing", "Bing"),
                            ("yahoo", "Yahoo"),
                        ],
                        default="google",
                        max_length=50,
                        verbose_name="Search Engine",
                    ),
                ),
                (
                    "checked_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Checked At"),
                ),
            ],
            options={
                "verbose_name": "Search Ranking",
                "verbose_name_plural": "Search Rankings",
                "ordering": ["-checked_at"],
            },
        ),
        migrations.CreateModel(
            name="SEOPageMeta",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created At"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated At"),
                ),
                ("url", models.URLField(unique=True, verbose_name="Page URL")),
                (
                    "meta_title",
                    models.CharField(max_length=200, verbose_name="Meta Title"),
                ),
                ("meta_description", models.TextField(verbose_name="Meta Description")),
                (
                    "meta_keywords",
                    models.TextField(blank=True, verbose_name="Meta Keywords"),
                ),
                (
                    "canonical_url",
                    models.URLField(blank=True, verbose_name="Canonical URL"),
                ),
                (
                    "no_index",
                    models.BooleanField(default=False, verbose_name="No Index"),
                ),
                (
                    "no_follow",
                    models.BooleanField(default=False, verbose_name="No Follow"),
                ),
            ],
            options={
                "verbose_name": "SEO Page Meta",
                "verbose_name_plural": "SEO Page Metadata",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="SEOSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created At"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated At"),
                ),
                (
                    "site_title",
                    models.CharField(max_length=200, verbose_name="Site Title"),
                ),
                ("site_description", models.TextField(verbose_name="Site Description")),
                (
                    "default_meta_keywords",
                    models.TextField(blank=True, verbose_name="Default Meta Keywords"),
                ),
                (
                    "robots_txt",
                    models.TextField(
                        default="User-agent: *\nDisallow:",
                        verbose_name="Robots.txt Rules",
                    ),
                ),
                (
                    "sitemap_url",
                    models.URLField(blank=True, verbose_name="Sitemap URL"),
                ),
                (
                    "canonical_url",
                    models.URLField(blank=True, verbose_name="Canonical URL"),
                ),
            ],
            options={
                "verbose_name": "SEO Settings",
                "verbose_name_plural": "SEO Settings",
            },
        ),
    ]
