# Generated by Django 5.1.4 on 2024-12-31 23:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AdCampaign",
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
                    "name",
                    models.CharField(max_length=255, verbose_name="Campaign Name"),
                ),
                (
                    "budget",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="Budget"
                    ),
                ),
                ("start_date", models.DateField(verbose_name="Start Date")),
                ("end_date", models.DateField(verbose_name="End Date")),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Is Active"),
                ),
            ],
            options={
                "verbose_name": "Ad Campaign",
                "verbose_name_plural": "Ad Campaigns",
                "ordering": ["-start_date", "name"],
            },
        ),
        migrations.CreateModel(
            name="AdPerformance",
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
                    "total_impressions",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Total Impressions"
                    ),
                ),
                (
                    "total_clicks",
                    models.PositiveIntegerField(default=0, verbose_name="Total Clicks"),
                ),
                (
                    "click_through_rate",
                    models.DecimalField(
                        decimal_places=2,
                        default=0.0,
                        max_digits=5,
                        verbose_name="Click-Through Rate (%)",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ad Performance",
                "verbose_name_plural": "Ad Performances",
            },
        ),
        migrations.CreateModel(
            name="AdPlacement",
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
                    "name",
                    models.CharField(max_length=255, verbose_name="Placement Name"),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Description"),
                ),
                (
                    "page",
                    models.CharField(
                        max_length=255,
                        verbose_name="Page (e.g., homepage, article page)",
                    ),
                ),
                (
                    "position",
                    models.CharField(
                        max_length=255, verbose_name="Position (e.g., header, sidebar)"
                    ),
                ),
                (
                    "dimensions",
                    models.CharField(
                        max_length=50, verbose_name="Ad Dimensions (e.g., 300x250)"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Is Active"),
                ),
            ],
            options={
                "verbose_name": "Ad Placement",
                "verbose_name_plural": "Ad Placements",
                "ordering": ["page", "position"],
            },
        ),
        migrations.CreateModel(
            name="Advertiser",
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
                    "name",
                    models.CharField(max_length=255, verbose_name="Advertiser Name"),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=254, unique=True, verbose_name="Email Address"
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True, max_length=15, verbose_name="Phone Number"
                    ),
                ),
                ("website", models.URLField(blank=True, verbose_name="Website")),
            ],
            options={
                "verbose_name": "Advertiser",
                "verbose_name_plural": "Advertisers",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Advertisement",
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
                ("name", models.CharField(max_length=255, verbose_name="Ad Name")),
                ("url", models.URLField(verbose_name="Target URL")),
                (
                    "impressions",
                    models.PositiveIntegerField(default=0, verbose_name="Impressions"),
                ),
                (
                    "clicks",
                    models.PositiveIntegerField(default=0, verbose_name="Clicks"),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Is Active"),
                ),
                ("start_date", models.DateField(verbose_name="Start Date")),
                ("end_date", models.DateField(verbose_name="End Date")),
                (
                    "campaign",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ads_campaign",
                        to="advertisements.adcampaign",
                        verbose_name="Campaign",
                    ),
                ),
            ],
            options={
                "verbose_name": "Advertisement",
                "verbose_name_plural": "Advertisements",
                "ordering": ["-start_date", "name"],
            },
        ),
    ]
