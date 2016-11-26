from regulations.generator.layers.base import ParagraphLayer
from regulations.generator.layers.utils import is_contained_in


class FootnotesLayer(ParagraphLayer):
    """Assembles the footnotes for this node, if available"""
    shorthand = 'footnotes'
    data_source = 'formatting'

    def __init__(self, layer, version=None):
        self.layer = layer
        self.version = version

    def attach_metadata(self, node):
        """
        Return a tuple of 'footnotes' and collection of footnotes.
        Footnotes are "collected" from the node and its children.
        .. note::
           This does not handle the case where the same note reference
           is used in multiple children.
        """
        footnotes = []
        for label in self.layer.keys():
            if is_contained_in(label, node['label_id']):
                footnotes += [x['footnote_data']
                              for x in self.layer[label]
                              if 'footnote_data' in x]
        node['footnotes'] = list(sorted(footnotes, key=lambda x: x['ref']))
