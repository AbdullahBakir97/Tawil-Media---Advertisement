from django.db import models
from django.utils import timezone

# Create your models here.

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'
        ordering = ['-created_at']

    def __str__(self):
        return self.email
