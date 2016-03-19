from django.template import loader

from regulations.generator.layers import utils
from regulations.generator.layers.base import SearchReplaceLayer


class GraphicsLayer(SearchReplaceLayer):
    shorthand = 'graphics'
    data_source = 'graphics'

    def __init__(self, layer):
        self.layer = layer
        self.template = loader.get_template('regulations/layers/graphics.html')

    def replacements_for(self, original, data):
        """Replace all instances of graphics with an img tag"""
        context = {'url': data['url'], 'alt': data['alt']}
        if 'thumb_url' in data:
            context['thumb_url'] = data['thumb_url']

        yield utils.render_template(self.template, context)
