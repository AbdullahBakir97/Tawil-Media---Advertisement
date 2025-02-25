from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "source.apps.users"
    
    def ready(self):
        import source.apps.users.signals
