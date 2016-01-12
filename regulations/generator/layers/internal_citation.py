from django.template import loader, Context

from regulations.generator.layers.base import InlineLayer
from regulations.generator.section_url import SectionUrl


class InternalCitationLayer(InlineLayer):
    shorthand = 'internal'
    data_source = 'internal-citations'

    def __init__(self, layer):
        self.layer = layer
        self.sectional = False
        self.version = None
        self.rev_urls = SectionUrl()
        self.rendered = {}

    def render_url(self, label, text,
                   template_name='regulations/layers/internal_citation.html'):

        key = (tuple(label), text, template_name)
        if key not in self.rendered:
            url = self.rev_urls.fetch(label, self.version, self.sectional)
            c = Context({'citation': {
                'url': url, 'label': text,
                'label_id': self.rev_urls.view_label_id(label, self.version)}})
            template = loader.get_template(template_name)
            self.rendered[key] = template.render(c).strip('\n')
        return self.rendered[key]

    def replacement_for(self, original, data):
        return self.render_url(data['citation'], original)
