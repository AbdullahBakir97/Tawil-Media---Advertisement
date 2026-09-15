from django import template

register = template.Library()


@register.filter
def times(count):
    """``{% for i in 3|times %}`` – iterate ``count`` times."""
    try:
        return range(int(count))
    except (TypeError, ValueError):
        return range(0)
