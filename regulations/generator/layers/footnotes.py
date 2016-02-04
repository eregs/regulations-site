from regulations.generator.layers.base import LayerBase


class FootnotesLayer(LayerBase):
    """Assembles the footnotes for this node, if available"""
    shorthand = 'footnotes'
    data_source = 'formatting'
    layer_type = LayerBase.PARAGRAPH

    def __init__(self, layer, version=None):
        self.layer = layer
        self.version = version

    def apply_layer(self, text_index):
        """Return a tuple of 'footnotes' and collection of footnotes"""
        footnotes = []
        for label in self.layer.keys():
            if label.startswith(text_index):
                footnotes += [x['footnote_data']
                              for x in self.layer[label]
                              if 'footnote_data' in x]
        return 'footnotes', sorted(footnotes, key=lambda x: x['ref'])
