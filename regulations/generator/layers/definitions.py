from django.template import loader

from regulations.generator.layers.base import InlineLayer
from regulations.generator.section_url import SectionUrl
from regulations.generator.layers import utils
from ..node_types import to_markup_id


class DefinitionsLayer(InlineLayer):
    shorthand = 'terms'
    data_source = 'terms'

    def __init__(self, layer):
        self.layer = layer
        self.template = loader.get_template(
            'regulations/layers/definition_citation.html')
        self.sectional = False
        self.version = None
        self.rev_urls = SectionUrl()
        self.rendered = {}
        # precomputation
        for def_struct in self.layer['referenced'].values():
            def_struct['reference_split'] = def_struct['reference'].split('-')

    def replacement_for(self, original, data):
        """ Create the link that takes you to the definition of the term. """
        citation = data['ref']
        # term = term w/o pluralization
        term = self.layer['referenced'][citation]['term']
        citation = self.layer['referenced'][citation]['reference_split']
        key = (original, tuple(citation))
        if key not in self.rendered:
            context = {'citation': {
                'url': self.rev_urls.fetch(citation, self.version,
                                           self.sectional),
                'label': original,
                'term': term,
                'definition_reference': '-'.join(to_markup_id(citation))}}
            rendered = utils.render_template(self.template, context)
            self.rendered[key] = rendered
        return self.rendered[key]
