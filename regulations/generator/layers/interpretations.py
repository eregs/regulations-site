from django.http import HttpRequest

#   Don't import PartialInterpView or utils directly; causes an import cycle
from regulations import generator, views
from regulations.generator.layers.base import ParagraphLayer
from regulations.generator.node_types import label_to_text
from regulations.generator.section_url import SectionUrl


class InterpretationsLayer(ParagraphLayer):
    """Fetches the (rendered) interpretation for this node, if available"""
    shorthand = 'interp'
    data_source = 'interpretations'

    def __init__(self, layer, version=None):
        self.layer = layer
        self.version = version
        self.section_url = SectionUrl()
        self.root_interp_label = None
        self.partial_view = None

    def preprocess_root(self, root):
        """The root label will allow us to use a single set of layer
        appliers and grab all interp data at once."""
        self.root_interp_label = '-'.join(root['label'] + ['Interp'])
        view_class = views.partial_interp.PartialInterpView
        self.partial_view = view_class.as_view(
            inline=True, layers=view_class.mk_layers(
                self.root_interp_label, self.version))

    def attach_metadata(self, node):
        """Return a pair of field-name + interpretation if one applies."""
        text_index = node['label_id']
        if text_index in self.layer and self.layer[text_index]:
            context = {'interps': [],
                       'for_markup_id': text_index,
                       'for_label': label_to_text(text_index.split('-'),
                                                  include_section=False)}
            #   Force caching of a few nodes up -- should prevent a request
            #   per interpretation if caching is on
            generator.generator.get_tree_paragraph(
                self.root_interp_label, self.version)
            for layer_element in self.layer[text_index]:
                reference = layer_element['reference']

                request = HttpRequest()
                request.method = 'GET'
                response = self.partial_view(request, label_id=reference,
                                             version=self.version)
                response.render()

                interp = {
                    'label_id': reference,
                    'markup': response.content,
                }

                ref_parts = reference.split('-')
                interp['section_id'] = self.section_url.interp(
                    ref_parts, self.version)

                context['interps'].append(interp)

            node['interp'] = context
