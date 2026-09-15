"""The newsletter composer: issues, their blocks, and per-subscriber tokens.

The unsubscribe token is added in the usual three steps for a unique column on
a table that already has rows: add it without the constraint, fill each row,
then make it unique.
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models


def give_each_subscriber_a_token(apps, schema_editor):
    model = apps.get_model("newsletter", "NewsletterSubscriber")
    for pk in model.objects.values_list("pk", flat=True).iterator():
        model.objects.filter(pk=pk).update(token=uuid.uuid4())


class Migration(migrations.Migration):
    dependencies = [
        ("newsletter", "0001_initial"),
        ("content", "0009_alter_category_options_category_accent_and_more"),
        ("events", "0001_initial"),
        ("studio", "0002_presskit_pressasset"),
    ]

    operations = [
        migrations.AddField(
            model_name="newslettersubscriber",
            name="language",
            field=models.CharField(
                choices=[("de", "German"), ("ar", "Arabic"), ("en", "English")],
                default="de",
                max_length=5,
                verbose_name="Language",
            ),
        ),
        migrations.AddField(
            model_name="newslettersubscriber",
            name="token",
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        migrations.RunPython(give_each_subscriber_a_token, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="newslettersubscriber",
            name="token",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.CreateModel(
            name="Issue",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("language", models.CharField(choices=[("de", "German"), ("ar", "Arabic"), ("en", "English")],
                                              default="de", max_length=5, verbose_name="Language")),
                ("subject", models.CharField(max_length=180, verbose_name="Subject")),
                ("preheader", models.CharField(blank=True, help_text="The line shown after the subject in the inbox.",
                                               max_length=180, verbose_name="Preheader")),
                ("intro", models.TextField(blank=True, help_text="A few lines from the desk.", verbose_name="Intro")),
                ("status", models.CharField(choices=[("draft", "Draft"), ("scheduled", "Scheduled"), ("sent", "Sent")],
                                            db_index=True, default="draft", max_length=12, verbose_name="Status")),
                ("scheduled_for", models.DateTimeField(blank=True, null=True, verbose_name="Goes out")),
                ("sent_at", models.DateTimeField(blank=True, editable=False, null=True, verbose_name="Sent")),
                ("sent_count", models.PositiveIntegerField(default=0, editable=False, verbose_name="Recipients")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Newsletter issue",
                "verbose_name_plural": "Newsletter issues",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="IssueBlock",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kind", models.CharField(
                    choices=[("lead", "Lead story"), ("article", "Article"), ("edition", "Edition"),
                             ("event", "Event"), ("ad", "Advertisement"), ("text", "Text")],
                    default="article", max_length=12, verbose_name="Kind")),
                ("order", models.PositiveSmallIntegerField(default=0, verbose_name="Order")),
                ("heading", models.CharField(blank=True, help_text="Leave empty to use the piece's own title.",
                                             max_length=180, verbose_name="Heading")),
                ("body", models.TextField(blank=True, verbose_name="Text")),
                ("ad_slot", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                              to="studio.adslot")),
                ("article", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                              to="content.article")),
                ("edition", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                              to="content.magazine")),
                ("event", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                            to="events.event")),
                ("issue", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="blocks",
                                            to="newsletter.issue")),
            ],
            options={"verbose_name": "Block", "verbose_name_plural": "Blocks", "ordering": ["order", "pk"]},
        ),
    ]
