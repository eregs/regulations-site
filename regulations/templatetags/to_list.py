"""Particularly when displaying bullets, it can be immensely helpful to
construct a list _within_ the template. Django's templates don't provide this
out of the box, so we need a new template tag. Suggestion from:
    http://stackoverflow.com/a/34407158

Usage:
    {% to_list "a" "b" "c" as my_list %}
    {% for el in my_list %}
        {{ el }}
    {% endfor %}
"""
from django import template

register = template.Library()


@register.assignment_tag
def to_list(*args):
    return args
