"""Replace the hand-rolled ``content.Tag`` model with django-taggit.

Django cannot ALTER an M2M field into a ``TaggableManager`` (different
``through`` model), so the field is dropped and re-added. Any tags stored in the
old ``content_article_tags`` table are discarded; the project had no production
data at this point.
"""

import taggit.managers
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0002_initial"),
        ("taggit", "0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="article",
            name="tags",
        ),
        migrations.DeleteModel(
            name="Tag",
        ),
        migrations.AddField(
            model_name="category",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="Is Active"),
        ),
        migrations.AddField(
            model_name="article",
            name="tags",
            field=taggit.managers.TaggableManager(
                blank=True,
                help_text="A comma-separated list of tags.",
                through="taggit.TaggedItem",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
    ]
