from django.utils.text import slugify
from django.core.exceptions import ValidationError


def generate_slug(value):
    return slugify(value)


def validate_article_data(title, content):
    if not title or not content:
        raise ValidationError("Title and content cannot be empty.")


def handle_media_upload(file, media_type, alt_text=''):
    # Logic to handle media uploads
    pass


def format_date(date):
    # Logic to format date for display
    return date.strftime('%Y-%m-%d')