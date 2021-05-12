from importlib import import_module

import six
from django.conf import settings
from django.urls import NoReverseMatch

from regulations.generator import api_reader


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
    def build_toc_urls(self, context, toc, node=None):
        if node is None:
            node = toc

        if any(node['type'] == x for x in ['subpart', 'section', 'subject_group']):
            try:
                identifier = '-'.join(node['identifier'])
                node['url'] = self.build_toc_url(context, toc, node) + "#" + identifier
            except NoReverseMatch:
                pass
        if node['children'] is not None:
            for child in node['children']:
                self.build_toc_urls(context, toc, child)

    def build_toc_url(self, context, toc, node):
        raise NotImplementedError()
