from django import template

register = template.Library()


@register.inclusion_tag('regulations/macros/nested.html')
def render_nested(template, context=None):
    ret = {'template': template}
    ret.update(context or {})
    return ret
