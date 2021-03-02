from django.views.generic.base import TemplateView

from regulations.views.mixins import TableOfContentsMixin
from regulations.generator.versions import get_versions


class RegulationLandingView(TableOfContentsMixin, TemplateView):

    template_name = "regulations/regulation_landing.html"

    sectional_links = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reg_part = self.kwargs.get("part")
        current, _ = get_versions(reg_part)
        reg_version = current['version']

        toc = self.get_toc(reg_part, reg_version)
        c = {
            'TOC': toc,
            'part': reg_part,
            'content': [
                'regulations/landing_%s.html' % reg_part,
                'regulations/landing_default.html',
            ],
        }
        return {**context, **c}
