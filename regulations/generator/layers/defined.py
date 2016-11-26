from django.template import loader, Context

from regulations.generator.layers.base import InlineLayer


class DefinedLayer(InlineLayer):
    shorthand = 'defined'
    data_source = 'terms'

    def __init__(self, layer):
        self.layer = layer
        self.template = loader.get_template('regulations/layers/defining.html')

    def replacement_for(self, original, data):
        """Noop: never called"""
        pass

    def apply_layer(self, text, text_index):
        """Catch all terms which are defined in this paragraph, replace them
        with a span"""
        layer_pairs = []
        for ref_struct in self.layer['referenced'].values():
            if text_index == ref_struct['reference']:
                pos = tuple(ref_struct['position'])
                original = text[pos[0]:pos[1]]
                context = Context({'term': original})
                replacement = self.template.render(context)
                replacement = replacement.strip('\n')
                layer_pairs.append((original, replacement, pos))
        return layer_pairs
