from django.template import loader

from regulations.generator.layers import utils
from regulations.generator.layers.base import SearchReplaceLayer


class ExternalCitationLayer(SearchReplaceLayer):
    shorthand = 'external'
    data_source = 'external-citations'

    def __init__(self, layer):
        self.layer = layer
        self.template = loader.get_template(
            'regulations/layers/external_citation.html')

    def replacements_for(self, text, data):
        yield utils.render_template(self.template, data)
