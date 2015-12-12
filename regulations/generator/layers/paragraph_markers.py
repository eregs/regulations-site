from django.template import loader
import utils

from regulations.generator.layers.base import SearchReplaceLayer


class ParagraphMarkersLayer(SearchReplaceLayer):
    shorthand = 'paragraph'
    data_source = 'paragraph-markers'

    def __init__(self, layer):
        self.layer = layer
        self.template = loader.get_template(
            'regulations/layers/paragraph_markers.html')

    def replacements_for(self, original, data):
        stripped = original.replace('(', '').replace(')', '').replace('.', '')

        context = {'paragraph': original, 'paragraph_stripped': stripped}
        yield utils.render_template(self.template, context)
