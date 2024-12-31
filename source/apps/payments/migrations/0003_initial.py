# Generated by Django 5.1.4 on 2024-12-31 23:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("payments", "0002_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payments",
                to=settings.AUTH_USER_MODEL,
                verbose_name="User",
            ),
        ),
        migrations.AddField(
            model_name="invoice",
            name="payment",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="invoice",
                to="payments.payment",
                verbose_name="Payment",
            ),
        ),
        migrations.AddField(
            model_name="payment",
            name="method",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="payments",
                to="payments.paymentmethod",
                verbose_name="Payment Method",
            ),
        ),
        migrations.AddField(
            model_name="refund",
            name="payment",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="refund",
                to="payments.payment",
                verbose_name="Payment",
            ),
        ),
    ]