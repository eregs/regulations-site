from django.views.generic.base import TemplateView
from django.http import Http404

from regulations.generator import generator
from regulations.generator.html_builder import CFRHTMLBuilder
from regulations.views import navigation, utils
from regulations.generator.node_types import EMPTYPART, REGTEXT, label_to_text



class SectionView(TemplateView):

    template_name = 'regulations/regulation-content.html'

    sectional_links = True

    def determine_layers(self, label_id, version):
        """Figure out which layers to apply by checking the GET args"""
        return generator.layers(
            utils.layer_names(self.request), 'cfr', label_id,
            self.sectional_links, version)
  
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # getting url info (label and version)
        # answering the question: what are we looking at?
        label_id = context['label_id']
        version = context['version']

        # do we have that data?
        tree = generator.get_tree_paragraph(label_id, version)
        if tree is None:
            raise Http404

        # unfortunatly rendering it...
        layers = list(self.determine_layers(label_id, version))
        builder = CFRHTMLBuilder(layers)
        builder.tree = tree
        builder.generate_html()

        # build context
        context['markup_page_type'] = 'reg-section'

        ## setting some kind of navigation
        context['navigation'] = self.neighboring_sections(
                label_id, version)

        ## build "context tree"
        child_of_root = builder.tree

        # Add a layer to account for subpart if this is regtext
        ## maybe to account for when a section isn't in a subpart
        ## e.g. 433.1 isn't under a subpart
        if builder.tree['node_type'] == REGTEXT:
            child_of_root = {
                'node_type': EMPTYPART,
                'children': [builder.tree]}
        
        context['tree'] = {'children': [child_of_root]}

        return context

    def neighboring_sections(self, label, version):
        nav_sections = navigation.nav_sections(label, version)
        if nav_sections:
            p_sect, n_sect = nav_sections

            return {'previous': p_sect, 'next': n_sect,
                    'page_type': 'reg-section'}