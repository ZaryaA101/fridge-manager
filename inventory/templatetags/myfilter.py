from django import template

register = template.Library()

@register.filter(name='addclass')
def addclass(value, arg):
    return value.as_widget(attrs={'class': arg})


@register.filter(name='addattributes')
def addattributes(value, args):
    """Add multiple attributes (e.g., class, id) to a form field."""
    attrs = {}
    for attr in args.split(','):
        key, val = attr.split('=')
        attrs[key.strip()] = val.strip()
    return value.as_widget(attrs=attrs)