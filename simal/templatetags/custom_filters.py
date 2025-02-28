from django import template

register = template.Library()


@register.filter(name="get_item")
def get_item(dictionary, key):
    """Get an item from a dictionary using a variable."""
    try:
        return dictionary.get(str(key))
    except Exception:
        return None
