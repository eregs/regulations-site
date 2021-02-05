from regulations.generator import generator, node_types
from regulations.views.partial import PartialView


class PartialInterpView(PartialView):
    """ Interpretation of a reg text section/paragraph or appendix. Used for
    in-line interpretations"""

    template_name = "regulations/interpretations.html"
    inline = False
    layers = []

    @staticmethod
    def mk_layers(root_label, version):
        """Function to generate a shared set of layers"""
        return generator.layers(
            ['terms', 'internal', 'keyterms', 'paragraph'], 'cfr', root_label,
            sectional=True, version=version)

    def determine_layers(self, label_id, version):
        """Don't generate new appliers"""
        return self.layers

    def transform_context(self, context, builder):
        context['inline'] = self.inline
        context['c'] = {'node_type': node_types.INTERP,
                        'children': [builder.tree]}
        return context
