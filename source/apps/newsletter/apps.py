from django.apps import AppConfig

class NewsletterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'source.apps.newsletter'
    verbose_name = 'Newsletter Management'
