from django.db import models
from django.utils import timezone
from source.apps.core.models import TimeStampedModel

class PaymentMethod(TimeStampedModel):
    name = models.CharField(max_length=100, verbose_name="Payment Method Name")
    provider = models.CharField(max_length=100, verbose_name="Provider Name")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    class Meta:
        verbose_name = "Payment Method"
        verbose_name_plural = "Payment Methods"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Payment(TimeStampedModel):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="payments", verbose_name="User"
    )
    subscription = models.ForeignKey(
        "subscriptions.Subscription", on_delete=models.SET_NULL, null=True, blank=True, related_name="payments", verbose_name="Subscription"
    )
    method = models.ForeignKey(
        PaymentMethod, on_delete=models.SET_NULL, null=True, related_name="payments", verbose_name="Payment Method"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Amount")
    currency = models.CharField(max_length=10, default="USD", verbose_name="Currency")
    status = models.CharField(
        max_length=20,
        choices=[
            ("success", "Success"),
            ("pending", "Pending"),
            ("failed", "Failed"),
        ],
        default="pending",
        verbose_name="Payment Status",
    )
    transaction_id = models.CharField(max_length=255, unique=True, verbose_name="Transaction ID")
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Payment Date")
    receipt_url = models.URLField(blank=True, verbose_name="Receipt URL")

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ["-payment_date"]

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.amount} {self.currency}"

    def mark_successful(self):
        """Mark the payment as successful."""
        self.status = "success"
        self.save()

    def mark_failed(self):
        """Mark the payment as failed."""
        self.status = "failed"
        self.save()

    def mark_pending(self):
        """Mark the payment as pending."""
        self.status = "pending"
        self.save()

    def get_receipt_url(self):
        """Retrieve the receipt URL."""
        return self.receipt_url


class Refund(TimeStampedModel):
    payment = models.OneToOneField(
        Payment, on_delete=models.CASCADE, related_name="refund", verbose_name="Payment"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Refund Amount")
    reason = models.TextField(verbose_name="Refund Reason")
    status = models.CharField(
        max_length=20,
        choices=[
            ("initiated", "Initiated"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ],
        default="initiated",
        verbose_name="Refund Status",
    )
    initiated_at = models.DateTimeField(auto_now_add=True, verbose_name="Initiated At")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Completed At")

    class Meta:
        verbose_name = "Refund"
        verbose_name_plural = "Refunds"
        ordering = ["-initiated_at"]

    def __str__(self):
        return f"Refund {self.payment.transaction_id} - {self.amount}"

    def complete_refund(self):
        """Mark the refund as completed."""
        self.status = "completed"
        self.completed_at = timezone.now()
        self.save()

    def initiate_refund(self):
        """Mark the refund as initiated."""
        self.status = "initiated"
        self.save()

    def cancel_refund(self):
        """Mark the refund as canceled."""
        self.status = "failed"
        self.save()


class Invoice(TimeStampedModel):
    payment = models.OneToOneField(
        Payment, on_delete=models.CASCADE, related_name="invoice", verbose_name="Payment"
    )
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name="Invoice Number")
    issued_date = models.DateTimeField(auto_now_add=True, verbose_name="Issued Date")
    due_date = models.DateTimeField(verbose_name="Due Date")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Amount")
    currency = models.CharField(max_length=10, default="USD", verbose_name="Currency")
    pdf_url = models.URLField(blank=True, verbose_name="Invoice PDF URL")

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        ordering = ["-issued_date"]

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.amount} {self.currency}"

    def send_invoice(self):
        """Simulate sending the invoice (expandable)."""
        print(f"Sending invoice {self.invoice_number} to user.")

    def mark_paid(self):
        """Mark the invoice as paid."""
        # Logic to mark the invoice as paid can be implemented here
        print(f"Invoice {self.invoice_number} marked as paid.")


class TransactionLog(TimeStampedModel):
    transaction_id = models.CharField(max_length=255, unique=True, verbose_name="Transaction ID")
    type = models.CharField(
        max_length=20,
        choices=[
            ("payment", "Payment"),
            ("refund", "Refund"),
        ],
        verbose_name="Transaction Type",
    )
    details = models.JSONField(verbose_name="Transaction Details")

    class Meta:
        verbose_name = "Transaction Log"
        verbose_name_plural = "Transaction Logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.type.capitalize()} Log - {self.transaction_id}"

    def log_transaction(self):
        """Log a new transaction."""
        print(f"Transaction logged: {self.transaction_id} of type {self.type}.")