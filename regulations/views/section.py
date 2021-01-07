from django.views.generic.base import TemplateView
from django.http import Http404

from regulations.generator import generator
from regulations.generator.html_builder import CFRHTMLBuilder
from regulations.generator.node_types import label_to_text, type_from_label
from regulations.views import navigation, utils
from regulations.generator.node_types import EMPTYPART, REGTEXT, label_to_text
from regulations.generator.versions import fetch_grouped_history
from regulations.generator.toc import fetch_toc
from regulations.generator.section_url import SectionUrl
from regulations.views.chrome import version_span



class SectionView(TemplateView):

    url_path_view = 'chrome_section_view'

    template_name = 'regulations/section.html'

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
        
        label_id_list = label_id.split('-')
        reg_part = label_id_list[0]
        context['formatted_id'] = label_to_text(label_id_list, True, True)

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

        # "chrome context"
        context['reg_part'] = reg_part
        context['history'] = fetch_grouped_history(reg_part)

        # table of contents
        toc = fetch_toc(reg_part, version)
        for el in toc:
            el['url'] = SectionUrl().of(
                el['index'], version, self.sectional_links)
            for sub in el.get('sub_toc', []):
                sub['url'] = SectionUrl().of(
                    sub['index'], version, self.sectional_links)
        context['TOC'] = toc

        # get meta data
        context['meta'] = utils.regulation_meta(reg_part, version)

        # Throw 404 if regulation doesn't exist
        if not context['meta']:
            raise error_handling.MissingContentException()

        # version context
        context['version_span'] = version_span(
            context['history'], context['meta']['effective_date'])
        context['version_switch_view'] = self.url_path_view

        # diff redirect
        context['diff_redirect_label'] = self.diff_redirect_label(
            context['label_id'], toc)

        return context

    def neighboring_sections(self, label, version):
        nav_sections = navigation.nav_sections(label, version)
        if nav_sections:
            p_sect, n_sect = nav_sections

            return {'previous': p_sect, 'next': n_sect,
                    'page_type': 'reg-section'}
    
    def diff_redirect_label(self, label_id, toc):
        """We only display diffs for sections and appendices. All other types
        of content must be converted to an appropriate diff label"""
        label_parts = label_id.split('-')
        if len(label_parts) == 1:   # whole CFR part. link to first section
            while toc:
                label_id = toc[0]['section_id']
                toc = toc[0].get('sub_toc')
        # We only show diffs for the whole interpretation at once
        elif 'Interp' in label_parts:
            label_id = label_parts[0] + '-Interp'
        # Non-section paragraph; link to the containing section
        elif len(label_parts) > 2:
            label_id = '-'.join(label_parts[:2])
        return label_id