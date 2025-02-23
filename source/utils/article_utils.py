from django.utils.text import slugify

def generate_slug(name):
    """Generate a slug for a given name."""
    return slugify(name)

def is_published(instance):
    """Check if an article or magazine is published."""
    return instance.is_published
