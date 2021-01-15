from django.views.generic.base import TemplateView
from django.http import Http404

from regulations.generator import generator
from regulations.generator.html_builder import CFRHTMLBuilder
from regulations.views import navigation, utils
from regulations.generator.node_types import EMPTYPART, REGTEXT, label_to_text
from regulations.generator.versions import fetch_grouped_history
from regulations.generator.toc import fetch_toc
from regulations.generator.section_url import SectionUrl
from regulations.views import error_handling
from regulations.views.chrome import version_span
from regulations.views.mixins import SidebarContextMixin


class SectionView(SidebarContextMixin, TemplateView):

    url_path_view = 'chrome_section_view'

    template_name = 'regulations/section.html'

    sectional_links = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # getting url info (label and version)
        # answering the question: what are we looking at?
        label_id = context['label_id']
        version = context['version']
        label_id_list = label_id.split('-')
        reg_part = label_id_list[0]
        toc = self.get_toc(reg_part, version)
        history = fetch_grouped_history(reg_part)
        meta = utils.regulation_meta(reg_part, version)

        if not meta:
            raise error_handling.MissingContentException()

        c = {
            'tree':                 self.get_tree(label_id, version),
            'markup_page_type':     'reg-section',
            'navigation':           self.get_neighboring_sections(label_id, version),
            'formatted_id':         label_to_text(label_id_list, True, True),
            'reg_part':             reg_part,
            'history':              history,
            'TOC':                  toc,
            'meta':                 meta,
            'version_span':         version_span(history, meta['effective_date']),
            'version_switch_view':  self.url_path_view,
            'diff_redirect_label':  label_id,
        }

        return {**context, **c}

    def get_tree(self, label_id, version):
        # do we have that data?
        tree = generator.get_tree_paragraph(label_id, version)
        if tree is None:
            raise Http404

        layers = list(self.determine_layers(label_id, version))
        builder = CFRHTMLBuilder(layers)
        builder.tree = tree
        builder.generate_html()

        child_of_root = builder.tree

        # Add a layer to account for subpart if this is regtext
        # maybe to account for when a section isn't in a subpart
        # e.g. 433.1 isn't under a subpart
        if builder.tree['node_type'] == REGTEXT:
            child_of_root = {
                'node_type': EMPTYPART,
                'children': [builder.tree]}

        return {'children': [child_of_root]}

    def determine_layers(self, label_id, version):
        """Figure out which layers to apply by checking the GET args"""
        return generator.layers(
            utils.layer_names(self.request), 'cfr', label_id,
            self.sectional_links, version)

    def get_neighboring_sections(self, label, version):
        nav_sections = navigation.nav_sections(label, version)
        if nav_sections:
            p_sect, n_sect = nav_sections
            return {'previous': p_sect, 'next': n_sect,
                    'page_type': 'reg-section'}

    def get_toc(self, reg_part, version):
        # table of contents
        toc = fetch_toc(reg_part, version)
        for el in toc:
            el['url'] = SectionUrl().of(
                el['index'], version, self.sectional_links)
            for sub in el.get('sub_toc', []):
                sub['url'] = SectionUrl().of(
                    sub['index'], version, self.sectional_links)
        return toc
