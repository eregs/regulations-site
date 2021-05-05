from django.views.generic.base import TemplateView

from regulations.generator.api_reader import ApiReader


class SearchView(TemplateView):

    template_name = 'regulations/search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        results = get_data(self.request.GET.get("q"))
        context['results'] = results
        return {**context, **self.request.GET.dict()}


def get_data(query):
    return ApiReader().v2_search(query)
