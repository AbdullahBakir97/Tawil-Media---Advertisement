from django.apps import AppConfig


class StudioConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "source.apps.studio"
    verbose_name = "Studio"

    def ready(self):
        from . import signals  # noqa: F401
