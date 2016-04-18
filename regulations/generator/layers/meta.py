from regulations.generator.layers.base import LayerBase
from regulations.generator.layers.utils import convert_to_python


class MetaLayer(LayerBase):
    shorthand = 'meta'
    data_source = 'meta'
    layer_type = LayerBase.PARAGRAPH

    def __init__(self, layer_data):
        self.layer_data = convert_to_python(layer_data)

    def apply_layer(self, text_index):
        """Return a pair of field-name (meta) + the layer data"""
        if self.layer_data.get(text_index):
            return 'meta', self.layer_data[text_index][0]
