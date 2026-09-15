"""The editorial workflow: status, schedule, desk note and a preview token.

Articles and editions that were already live keep their status as published, so
nothing disappears from the site the moment this lands. The preview token is
added without its unique constraint, filled in one row at a time, and only then
made unique — the usual three steps for a unique column on a table with rows.
"""

import uuid

from django.db import migrations, models


def give_each_row_a_token(apps, schema_editor):
    for name in ("Article", "Magazine"):
        model = apps.get_model("content", name)
        for pk in model.objects.values_list("pk", flat=True).iterator():
            model.objects.filter(pk=pk).update(preview_token=uuid.uuid4())


def keep_published_rows_published(apps, schema_editor):
    for name in ("Article", "Magazine"):
        model = apps.get_model("content", name)
        model.objects.filter(is_published=True).update(status="published")


def back_to_draft(apps, schema_editor):
    """Reversing only drops the new columns; nothing to undo in the data."""


class Migration(migrations.Migration):
    dependencies = [("content", "0007_media_caption_media_credit_media_focal_x_and_more")]

    operations = [
        *[
            migrations.AddField(
                model_name=model,
                name="status",
                field=models.CharField(
                    choices=[
                        ("draft", "Draft"),
                        ("review", "In review"),
                        ("scheduled", "Scheduled"),
                        ("published", "Published"),
                    ],
                    db_index=True,
                    default="draft",
                    max_length=16,
                    verbose_name="Status",
                ),
            )
            for model in ("article", "magazine")
        ],
        *[
            migrations.AddField(
                model_name=model,
                name="scheduled_for",
                field=models.DateTimeField(
                    blank=True, help_text="Leave empty to publish by hand.", null=True, verbose_name="Goes live"
                ),
            )
            for model in ("article", "magazine")
        ],
        *[
            migrations.AddField(
                model_name=model,
                name="editor_note",
                field=models.CharField(
                    blank=True,
                    help_text="What is still missing, for the desk only.",
                    max_length=255,
                    verbose_name="Desk note",
                ),
            )
            for model in ("article", "magazine")
        ],
        *[
            migrations.AddField(
                model_name=model,
                name="preview_token",
                field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
            )
            for model in ("article", "magazine")
        ],
        migrations.RunPython(give_each_row_a_token, migrations.RunPython.noop),
        migrations.RunPython(keep_published_rows_published, back_to_draft),
        *[
            migrations.AlterField(
                model_name=model,
                name="preview_token",
                field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
            )
            for model in ("article", "magazine")
        ],
    ]
