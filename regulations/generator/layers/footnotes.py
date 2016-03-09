from regulations.generator.layers.base import LayerBase
from regulations.generator.layers.utils import is_contained_in


class FootnotesLayer(LayerBase):
    """Assembles the footnotes for this node, if available"""
    shorthand = 'footnotes'
    data_source = 'formatting'
    layer_type = LayerBase.PARAGRAPH

    def __init__(self, layer, version=None):
        self.layer = layer
        self.version = version

    def apply_layer(self, text_index):
        """
        Return a tuple of 'footnotes' and collection of footnotes.
        Footnotes are "collected" from the node and its children.
        .. note::
           This does not handle the case where the same note reference
           is used in multiple children.
        """
        footnotes = []
        for label in self.layer.keys():
            if is_contained_in(label, text_index):
                footnotes += [x['footnote_data']
                              for x in self.layer[label]
                              if 'footnote_data' in x]
        return 'footnotes', sorted(footnotes, key=lambda x: x['ref'])
