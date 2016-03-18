from importlib import import_module

import six
from django.conf import settings
from django.views.generic.base import TemplateView

from regulations.generator import api_reader


class SideBarView(TemplateView):
    """ View for handling the right-side sidebar """
    template_name = 'regulations/sidebar.html'
    # contains either class paths or class objects (not instances)
    components = settings.SIDEBARS

    def get_context_data(self, **kwargs):
        context = super(SideBarView, self).get_context_data(**kwargs)

        client = api_reader.ApiReader()

        klasses = []
        for class_or_class_path in self.components:
            if isinstance(class_or_class_path, six.string_types):
                module, class_name = class_or_class_path.rsplit('.', 1)
                klasses.append(getattr(import_module(module), class_name))
            else:
                klasses.append(class_or_class_path)

        sidebars = [klass(context['label_id'], context['version'])
                    for klass in klasses]
        context['sidebars'] = [sidebar.full_context(client, self.request)
                               for sidebar in sidebars]

        return context
