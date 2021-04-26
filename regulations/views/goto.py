from django.urls import reverse
from django.http import Http404
from django.views.generic.base import RedirectView
from regulations.views.utils import find_subpart
from regulations.views.mixins import TableOfContentsMixin
from regulations.views.errors import NotInSubpart


class GoToRedirectView(TableOfContentsMixin, RedirectView):

    permanent = False
    pattern_name = 'reader_view'

    def get_redirect_url(self, *args, **kwargs):
        kwargs = self.request.GET.dict()
        url_kwargs = {
                "part": kwargs.get("part"),
                "version": kwargs.get("version"),
        }
        toc = self.get_toc(url_kwargs["part"], url_kwargs["version"])
        try:
            subpart = find_subpart(kwargs.get("section"), toc)
            if subpart is None:
                raise Http404()
            url_kwargs["subpart"] = subpart
        except NotInSubpart:
            pass
        citation = url_kwargs["part"] + '-' + kwargs["section"]
        url = reverse(self.pattern_name, kwargs=url_kwargs) + "#" + citation
        return url
