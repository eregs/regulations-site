from importlib import import_module

import six
from django.conf import settings

from regulations.generator import api_reader


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
