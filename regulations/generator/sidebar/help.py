from django.template import TemplateDoesNotExist
from django.template.loader import get_template

from regulations.generator.sidebar.base import SidebarBase
# @todo - seems like code in `generator` shouldn't reach in to `views`?
from regulations.views.utils import layer_names


class Help(SidebarBase):
    """Help info; composed of subtemplates defined by the active layers"""
    shorthand = 'help'

    def context(self, http_client, request):
        subtemplates = []
        for layer_name in sorted(layer_names(request)):
            template_name = 'regulations/sidebar/help/{}.html'.format(
                layer_name)
            try:
                template = get_template(template_name)
                subtemplates.append(template.render(
                    {'cfr_part': self.cfr_part}))
            except TemplateDoesNotExist:
                pass
        return {'subtemplates': subtemplates}
