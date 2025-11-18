from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    """
    Adds the given CSS class string to a Django form field widget.
    Usage in template:
        {{ form.username|add_class:"w-full p-2 border rounded" }}
    """
    return field.as_widget(attrs={"class": css})
