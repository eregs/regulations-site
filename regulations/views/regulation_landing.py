from datetime import date
from requests import HTTPError
from django.views.generic.base import TemplateView
from django.http import Http404

from regulations.generator import api_reader

client = api_reader.ApiReader()


class RegulationLandingView(TemplateView):

    template_name = "regulations/regulation_landing.html"

    sectional_links = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reg_part = self.kwargs.get("part")

        try:
            current = client.v2_part(date.today(), 42, reg_part)
        except HTTPError:
            raise Http404

        reg_version = current['date']

        c = {
            'structure': current['structure']['children'][0]['children'][0]['children'][0],
            'version': reg_version,
            'part': reg_part,
            'content': [
                'regulations/partials/landing_%s.html' % reg_part,
                'regulations/partials/landing_default.html',
            ],
        }
        return {**context, **c}

    def get_toc(self, part, date):
        return {}
