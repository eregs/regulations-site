import re
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape

register = template.Library()

el = ('<span class="search-highlight">', '</span>')


@register.filter(name='highlight', needs_autoescape=True, is_safe=True)
@stringfilter
def highlight(text, arg,  autoescape=True):
    if autoescape:
        text = conditional_escape(text)
    search_terms = arg.split()
    for term in search_terms:
        text = wrap(term, el, text)
    # Used to highlight search results originating
    # from internal data sources, low risk of XSS.
    # Also escapes the input first, only html being
    # returned is generated within this function.
    return mark_safe(text)  # nosec


def wrap(term, el, text):
    re_term = re.compile(rf"{term}", re.IGNORECASE)
    result = set(re_term.findall(text))
    for match in result:
        wrapped = f'{el[0]}{match}{el[1]}'
        text = text.replace(match, wrapped)
    return text
