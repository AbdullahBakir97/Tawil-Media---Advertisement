from django import template

register = template.Library()


@register.filter
def elided_range(page_obj, on_each_side=1):
    """``{% for num in page_obj|elided_range %}`` – page numbers with ellipses around the current page."""
    return page_obj.paginator.get_elided_page_range(page_obj.number, on_each_side=on_each_side, on_ends=1)


@register.filter
def times(count):
    """``{% for i in 3|times %}`` – iterate ``count`` times."""
    try:
        return range(int(count))
    except (TypeError, ValueError):
        return range(0)
