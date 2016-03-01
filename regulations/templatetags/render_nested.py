from django.template import Library, Context, loader

register = Library()


@register.simple_tag()
def render_nested(template, context=None):
    return loader.get_template(template).render(Context(context))
