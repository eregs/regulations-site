from requests import HTTPError

from django.urls import reverse
from django.http import Http404
from django.views.generic.base import RedirectView

from regulations.views.utils import find_subpart
from regulations.views.mixins import TableOfContentsMixin
from regulations.views.errors import NotInSubpart
from regulations.generator import api_reader

client = api_reader.ApiReader()


class GoToRedirectView(TableOfContentsMixin, RedirectView):

    permanent = False
    pattern_name = 'reader_view'

    def get_redirect_url(self, *args, **kwargs):
        kwargs = self.request.GET.dict()
        url_kwargs = {
                "part": kwargs.get("part"),
                "version": kwargs.get("version"),
        }

        try:
            toc = client.toc(url_kwargs['version'], 42, url_kwargs['part'])['toc']
        except HTTPError:
            raise Http404

        try:
            subpart = find_subpart(kwargs.get("section"), toc)
            if subpart is None:
                raise Http404()
            url_kwargs["subpart"] = "Subpart-{}".format(subpart)
        except NotInSubpart:
            pass
        citation = url_kwargs["part"] + '-' + kwargs["section"]
        url = reverse(self.pattern_name, kwargs=url_kwargs) + "#" + citation
        return url
