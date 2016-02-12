from django import template

register = template.Library()


@register.inclusion_tag('regulations/macros/external_link.html')
def external_link(url, text, classes=""):
    return {"url": url, "text": text, "classes": classes}
