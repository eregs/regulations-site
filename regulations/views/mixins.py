from importlib import import_module

import six
from django.conf import settings
from django.urls import reverse, NoReverseMatch

from regulations.generator import api_reader
from regulations.generator.toc import fetch_toc


def build_citation(context):
    citation = []
    if 'part' in context:
        citation.append(context["part"])
        if 'section' in context:
            citation.append(context["section"])
        elif 'subpart' in context:
            citation.append(context["subpart"])
    return citation


class CitationContextMixin:
    def get_context_data(self, **kwargs):
        context = super(CitationContextMixin, self).get_context_data(**kwargs)
        context['citation'] = build_citation(context)
        return context


class SidebarContextMixin():
    # contains either class paths or class objects (not instances)
    sidebar_classes = settings.SIDEBARS
    client = api_reader.ApiReader()

    def get_context_data(self, **kwargs):
        context = super(SidebarContextMixin, self).get_context_data(**kwargs)

        sidebars = []
        for class_or_class_path in self.sidebar_classes:
            sidebars.append(
                self.build_sidebar_context(
                    class_or_class_path,
                    build_citation(context),
                    context['version']))

        context['sidebars'] = sidebars

        return context

    def build_sidebar_context(self, sidebar_class, label_id, version):
        if isinstance(sidebar_class, six.string_types):
            module_name, class_name = sidebar_class.rsplit('.', 1)
            sidebar_class = getattr(import_module(module_name), class_name)
        sidebar = sidebar_class(label_id, version)
        return sidebar.full_context(self.client, self.request)


class TableOfContentsMixin:
    default_view = 'reader_view'

    def get_toc(self, reg_part, version):
        # table of contents
        toc = fetch_toc(reg_part, version)
        self.build_urls(toc, version)
        return toc

    def build_urls(self, toc, version, subpart=None):
        for el in toc:
            try:
                part = el['index'][0]
                section = el['index'][1]
                el['url'] = self.build_toc_url(part, subpart, section, version) + '#' + part + '-' + section
            except NoReverseMatch:
                el['url'] = ''

            if 'sub_toc' in el:
                if 'Subpart' in el['index']:
                    self.build_urls(el['sub_toc'], version, '-'.join(el['index'][1:]))
                else:
                    self.build_urls(el['sub_toc'], version, subpart)

    def build_toc_url(self, part, subpart, section, version):
        return reverse(self.default_view, args=(part, subpart or section, version))
