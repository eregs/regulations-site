import re

from django.template import loader

from regulations.generator.layers import utils
from regulations.generator.layers.base import (
    ParagraphLayer, SearchReplaceLayer)


class ParagraphMarkersLayer(SearchReplaceLayer):
    """This layer creates a new paragraph marker (with periods) and adds a
    class to the old (to make it easier to hide). It exists for backwards
    compatibility; new clients should be using MarkerHidingLayer and
    MarkerInfoLayer instead"""
    shorthand = 'paragraph'
    data_source = 'paragraph-markers'
    TO_STRIP_RE = re.compile(r'[().]')

    def __init__(self, layer):
        self.layer = layer
        self.template = loader.get_template(
            'regulations/layers/paragraph_markers.html')

    def replacements_for(self, original, data):
        stripped = self.TO_STRIP_RE.sub('', original)

        context = {'paragraph': original, 'paragraph_stripped': stripped}
        yield utils.render_template(self.template, context)


class MarkerHidingLayer(SearchReplaceLayer):
    """This layer wraps the original marker in a class, making it easier to
    hide."""
    shorthand = 'marker-hiding'
    data_source = 'paragraph-markers'

    def __init__(self, layer):
        self.layer = layer
        self.template = loader.get_template(
            'regulations/layers/marker_hiding.html')

    def replacements_for(self, original, data):
        context = {'paragraph': original}
        yield utils.render_template(self.template, context)


class MarkerInfoLayer(ParagraphLayer):
    """This layer adds the paragraph marker as an attribute of the node. This
    is then used to display the marker outside of the normal position"""
    shorthand = 'marker-info'
    data_source = 'paragraph-markers'

    def __init__(self, layer):
        self.layer_data = layer

    def attach_metadata(self, node):
        text_index = node['label_id']
        if self.layer_data.get(text_index):
            original = self.layer_data[text_index][0]["text"]
            stripped = original.replace('(', '').replace(')', '')
            stripped = stripped.replace('.', '')
            node['paragraph_marker'] = stripped
