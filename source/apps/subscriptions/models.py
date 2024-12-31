from django.db import models
from source.apps.core.models import TimeStampedModel

class SubscriptionPlan(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name="Plan Name")
    description = models.TextField(blank=True, verbose_name="Plan Description")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price (per billing cycle)")
    billing_cycle = models.CharField(
        max_length=50,
        choices=[
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
            ("yearly", "Yearly"),
        ],
        default="monthly",
        verbose_name="Billing Cycle",
    )
    features = models.JSONField(blank=True, null=True, verbose_name="Plan Features")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    class Meta:
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"
        ordering = ["price"]

    def __str__(self):
        return self.name

    def update_plan(self, name=None, description=None, price=None, billing_cycle=None):
        """Update the subscription plan details."""
        if name:
            self.name = name
        if description:
            self.description = description
        if price is not None:
            self.price = price
        if billing_cycle:
            self.billing_cycle = billing_cycle
        self.save()


class Subscription(TimeStampedModel):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="subscriptions", verbose_name="User"
    )
    plan = models.ForeignKey(
        SubscriptionPlan, on_delete=models.SET_NULL, null=True, related_name="subscriptions", verbose_name="Plan"
    )
    start_date = models.DateField(auto_now_add=True, verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    auto_renew = models.BooleanField(default=True, verbose_name="Auto Renew")

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.user} - {self.plan}"

    def deactivate(self):
        """Deactivate the subscription."""
        self.is_active = False
        self.save()

    def renew_subscription(self, new_end_date):
        """Renew the subscription by setting a new end date."""
        self.end_date = new_end_date
        self.is_active = True
        self.save()

    def cancel_subscription(self):
        """Cancel the subscription."""
        self.is_active = False
        self.save()


class Billing(TimeStampedModel):
    subscription = models.ForeignKey(
        Subscription, on_delete=models.CASCADE, related_name="billings", verbose_name="Subscription"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Amount")
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Payment Date")
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ("credit_card", "Credit Card"),
            ("paypal", "PayPal"),
            ("bank_transfer", "Bank Transfer"),
        ],
        default="credit_card",
        verbose_name="Payment Method",
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("paid", "Paid"),
            ("pending", "Pending"),
            ("failed", "Failed"),
        ],
        default="pending",
        verbose_name="Payment Status",
    )
    receipt_url = models.URLField(blank=True, verbose_name="Receipt URL")

    class Meta:
        verbose_name = "Billing"
        verbose_name_plural = "Billing Records"
        ordering = ["-payment_date"]

    def __str__(self):
        return f"Billing for {self.subscription} - {self.payment_date}"

    def mark_paid(self):
        """Mark the billing as paid."""
        self.status = "paid"
        self.save()

    def mark_failed(self):
        """Mark the billing as failed."""
        self.status = "failed"
        self.save()


class FeatureAccess(TimeStampedModel):
    plan = models.ForeignKey(
        SubscriptionPlan, on_delete=models.CASCADE, related_name="feature_access", verbose_name="Plan"
    )
    feature_name = models.CharField(max_length=255, verbose_name="Feature Name")
    description = models.TextField(blank=True, verbose_name="Feature Description")
    is_available = models.BooleanField(default=True, verbose_name="Is Available")

    class Meta:
        verbose_name = "Feature Access"
        verbose_name_plural = "Feature Access Records"
        unique_together = ("plan", "feature_name")
        ordering = ["plan", "feature_name"]

    def __str__(self):
        return f"{self.feature_name} ({self.plan})"

    def toggle_availability(self):
        """Toggle the availability of the feature."""
        self.is_available = not self.is_available
        self.save()


class DiscountCode(TimeStampedModel):
    code = models.CharField(max_length=50, unique=True, verbose_name="Discount Code")
    plan = models.ForeignKey(
        SubscriptionPlan, on_delete=models.CASCADE, related_name="discounts", verbose_name="Plan"
    )
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Discount Percentage"
    )
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    class Meta:
        verbose_name = "Discount Code"
        verbose_name_plural = "Discount Codes"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.code} ({self.discount_percentage}%)"

    def activate(self):
        """Activate the discount code."""
        self.is_active = True
        self.save()

    def deactivate(self):
        """Deactivate the discount code."""
        self.is_active = False
        self.save()