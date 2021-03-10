from django.views.generic.base import TemplateView
from django.http import Http404
from django.urls import reverse

from regulations.generator import api_reader
from regulations.generator import generator
from regulations.views import navigation, utils
from regulations.views import error_handling
from regulations.views.mixins import SidebarContextMixin, CitationContextMixin, TableOfContentsMixin


class ReaderView(TableOfContentsMixin, SidebarContextMixin, CitationContextMixin, TemplateView):

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
            'tree':         tree,
            'navigation':   self.get_neighboring_sections(reg_citation, reg_version),
            'reg_part':     reg_part,
            'meta':         meta,
            'TOC':          toc,
        }

        links = self.get_view_links(context, toc)

        return {**context, **c, **links}

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

    def get_view_links(self, context, toc):
        raise NotImplementedError()


class PartReaderView(ReaderView):
    def get_view_links(self, context, toc):
        part = context['part']
        version = context['version']
        first_section = utils.first_section(part, version)
        first_subpart = utils.first_subpart(part, version)

        return {
            'subpart_view_link': reverse('subpart_reader_view', args=(part, first_subpart, version)),
            'section_view_link': reverse('section_reader_view', args=(part, first_section, version)),
        }

    def build_toc_url(self, part, subpart, section, version):
        return reverse('part_reader_view', args=(part, version))


class SubpartReaderView(ReaderView):
    def get_view_links(self, context, toc):
        part = context['part']
        version = context['version']
        subpart = context['subpart']
        section = utils.find_subpart_first_section(subpart, toc)
        if section is None:
            section = utils.first_section(part, version)
        citation = part + '-' + section

        return {
            'part_view_link': reverse('part_reader_view', args=(part, version)) + '#' + citation,
            'section_view_link': reverse('section_reader_view', args=(part, section, version)),
        }

    def build_toc_url(self, part, subpart, section, version):
        return reverse('subpart_reader_view', args=(part, subpart, version))


class SectionReaderView(ReaderView):
    def get_view_links(self, context, toc):
        part = context['part']
        section = context['section']
        version = context['version']
        citation = context['citation']
        subpart = utils.find_subpart(section, toc)
        if subpart is None:
            subpart = utils.first_subpart(part, version)

        return {
            'part_view_link': reverse('part_reader_view', args=(part, version)) + '#' + citation,
            'subpart_view_link': reverse('subpart_reader_view', args=(part, subpart, version)) + '#' + citation,
        }
