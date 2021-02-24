from django.views.generic.base import TemplateView
from django.http import Http404

from regulations.generator import api_reader
from regulations.generator import generator
from regulations.views import navigation, utils
from regulations.generator.toc import fetch_toc
from regulations.generator.section_url import SectionUrl
from regulations.views import error_handling
from regulations.views.mixins import SidebarContextMixin, CitationContextMixin


class SectionView(SidebarContextMixin, CitationContextMixin, TemplateView):

    template_name = 'regulations/section.html'

    sectional_links = True

    client = api_reader.ApiReader()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # getting url info (label and version)
        # answering the question: what are we looking at?
        reg_version = context["version"]
        reg_part = context["part"]
        reg_citation = context["citation"]
        toc = self.get_toc(reg_part, reg_version)
        meta = utils.regulation_meta(reg_part, reg_version)
        tree = self.get_regulation(reg_citation, reg_version)

        if not meta:
            raise error_handling.MissingContentException()

        c = {
            'tree':                 tree,
            'navigation':           self.get_neighboring_sections(reg_citation, reg_version),
            'reg_part':             reg_part,
            'TOC':                  toc,
            'meta':                 meta,
        }

        return {**context, **c}

    def get_regulation(self, label_id, version):
        regulation = self.client.regulation(label_id, version)
        if regulation is None:
            raise Http404
        return regulation

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
        self.build_urls(toc, version)
        return toc

    def build_urls(self, toc, version):
        for el in toc:
            el['url'] = SectionUrl().of(
                el['index'], version, self.sectional_links)
            if 'sub_toc' in el:
                self.build_urls(el['sub_toc'], version)
