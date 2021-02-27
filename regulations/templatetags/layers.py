from django import template
from django.urls import reverse, NoReverseMatch
from regulations.generator import api_reader

register = template.Library()


@register.filter(name='internalcitation')
def internalcitation(value, arg):
    if value == "":
        return value
    version = arg['version']
    citation_template = template.loader.get_template('regulations/layers/internal_citation.html')
    label = "-".join(arg['label'])
    result = api_reader.ApiReader().layer("internal-citations", "cfr", label, version)
    if result is not None and label in result:
        citations = result[label]
        citations.sort(key=lambda x: x["offsets"][0][0], reverse=True)
        for citation in citations:
            original = value[citation["offsets"][0][0]:citation["offsets"][0][1]]
            try:
                # /433/section/112#433-112-c
                url = reverse("reader_view", args=[*citation["citation"][:2], version]) + "#" + "-".join(citation["citation"])
                context = {
                    "citation": citation["citation"],
                    "original": original,
                    "url": url,
                }
                rendered_citation = citation_template.render(context)
                value = value[:citation["offsets"][0][0]] + rendered_citation + value[citation["offsets"][0][1]:]
            except NoReverseMatch:
                pass
        return value
    return value
