from django.urls import reverse
from django.views.generic.base import RedirectView


class GoToRedirectView(RedirectView):

    permanent = False
    pattern_name = 'section_reader_view'

    def get_redirect_url(self, *args, **kwargs):
        kwargs = self.request.GET.dict()
        url = reverse(self.pattern_name, kwargs=kwargs)
        return url
