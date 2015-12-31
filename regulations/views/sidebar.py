from importlib import import_module

from django.conf import settings
from django.views.generic.base import TemplateView

from regulations.generator import api_reader


class SideBarView(TemplateView):
    """ View for handling the right-side sidebar """
    def get_template_names(self):
        return ['regulations/custom-sidebar.html', 'regulations/sidebar.html']

    def get_context_data(self, **kwargs):
        context = super(SideBarView, self).get_context_data(**kwargs)

        client = api_reader.ApiReader()

        context['sidebars'] = []
        for class_path in settings.SIDEBARS:
            module, class_name = class_path.rsplit('.', 1)
            klass = getattr(import_module(module), class_name)
            sidebar = klass(context['label_id'], context['version'])
            context['sidebars'].append(
                sidebar.full_context(client, self.request))

        return context
