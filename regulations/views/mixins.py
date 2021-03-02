from importlib import import_module

import six
from django.conf import settings

from regulations.generator import api_reader
from regulations.generator.toc import fetch_toc
from regulations.generator.section_url import SectionUrl


class SidebarContextMixin:
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
                    f"{context['part']}-{context['section']}",
                    context['version']))

        context['sidebars'] = sidebars

        return context

    def build_sidebar_context(self, sidebar_class, label_id, version):
        if isinstance(sidebar_class, six.string_types):
            module_name, class_name = sidebar_class.rsplit('.', 1)
            sidebar_class = getattr(import_module(module_name), class_name)
        sidebar = sidebar_class(label_id, version)
        return sidebar.full_context(self.client, self.request)


class CitationContextMixin:
    def get_context_data(self, **kwargs):
        context = super(CitationContextMixin, self).get_context_data(**kwargs)
        if 'part' in context and 'section' in context:
            context['citation'] = f"{context['part']}-{context['section']}"
        return context


class TableOfContentsMixin:
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
