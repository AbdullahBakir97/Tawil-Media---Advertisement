from django.apps import AppConfig

class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'source.apps.notifications'
    label = 'notifications'

    def ready(self):
        import source.apps.notifications.signals  # noqa
