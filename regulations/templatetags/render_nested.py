from django.template import Library, loader

register = Library()


@register.simple_tag()
def render_nested(*templates, context=None, **kwargs):
    return loader.select_template(templates).render(context or kwargs)


@register.filter
def interpolate(value, arg):
    try:
        return value.format(**arg)
    except:
        return value
