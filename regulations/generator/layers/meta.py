from regulations.generator.layers.base import ParagraphLayer
from regulations.generator.layers.utils import convert_to_python


class MetaLayer(ParagraphLayer):
    shorthand = 'meta'
    data_source = 'meta'

    def __init__(self, layer_data):
        self.layer_data = convert_to_python(layer_data)

    def attach_metadata(self, node):
        """Return a pair of field-name (meta) + the layer data"""
        text_index = node['label_id']
        if self.layer_data.get(text_index):
            node['meta'] = self.layer_data[text_index][0]
