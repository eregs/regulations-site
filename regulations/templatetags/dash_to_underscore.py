# vim: set encoding=utf-8
from django import template

register = template.Library()


@register.filter()
def dash_to_underscore(value):
    return value.replace("-", "_")
