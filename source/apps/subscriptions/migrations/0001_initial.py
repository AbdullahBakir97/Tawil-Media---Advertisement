# Generated by Django 5.1.4 on 2024-12-31 23:26

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Billing",
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
                    "amount",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="Amount"
                    ),
                ),
                (
                    "payment_date",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Payment Date"
                    ),
                ),
                (
                    "payment_method",
                    models.CharField(
                        choices=[
                            ("credit_card", "Credit Card"),
                            ("paypal", "PayPal"),
                            ("bank_transfer", "Bank Transfer"),
                        ],
                        default="credit_card",
                        max_length=50,
                        verbose_name="Payment Method",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("paid", "Paid"),
                            ("pending", "Pending"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="Payment Status",
                    ),
                ),
                (
                    "receipt_url",
                    models.URLField(blank=True, verbose_name="Receipt URL"),
                ),
            ],
            options={
                "verbose_name": "Billing",
                "verbose_name_plural": "Billing Records",
                "ordering": ["-payment_date"],
            },
        ),
        migrations.CreateModel(
            name="DiscountCode",
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
                    "code",
                    models.CharField(
                        max_length=50, unique=True, verbose_name="Discount Code"
                    ),
                ),
                (
                    "discount_percentage",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=5,
                        verbose_name="Discount Percentage",
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
                "verbose_name": "Discount Code",
                "verbose_name_plural": "Discount Codes",
                "ordering": ["-start_date"],
            },
        ),
        migrations.CreateModel(
            name="FeatureAccess",
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
                    "feature_name",
                    models.CharField(max_length=255, verbose_name="Feature Name"),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Feature Description"),
                ),
                (
                    "is_available",
                    models.BooleanField(default=True, verbose_name="Is Available"),
                ),
            ],
            options={
                "verbose_name": "Feature Access",
                "verbose_name_plural": "Feature Access Records",
                "ordering": ["plan", "feature_name"],
            },
        ),
        migrations.CreateModel(
            name="Subscription",
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
                    "start_date",
                    models.DateField(auto_now_add=True, verbose_name="Start Date"),
                ),
                ("end_date", models.DateField(verbose_name="End Date")),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Is Active"),
                ),
                (
                    "auto_renew",
                    models.BooleanField(default=True, verbose_name="Auto Renew"),
                ),
            ],
            options={
                "verbose_name": "Subscription",
                "verbose_name_plural": "Subscriptions",
                "ordering": ["-start_date"],
            },
        ),
        migrations.CreateModel(
            name="SubscriptionPlan",
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
                ("name", models.CharField(max_length=255, verbose_name="Plan Name")),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Plan Description"),
                ),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        verbose_name="Price (per billing cycle)",
                    ),
                ),
                (
                    "billing_cycle",
                    models.CharField(
                        choices=[
                            ("daily", "Daily"),
                            ("weekly", "Weekly"),
                            ("monthly", "Monthly"),
                            ("yearly", "Yearly"),
                        ],
                        default="monthly",
                        max_length=50,
                        verbose_name="Billing Cycle",
                    ),
                ),
                (
                    "features",
                    models.JSONField(
                        blank=True, null=True, verbose_name="Plan Features"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Is Active"),
                ),
            ],
            options={
                "verbose_name": "Subscription Plan",
                "verbose_name_plural": "Subscription Plans",
                "ordering": ["price"],
            },
        ),
    ]