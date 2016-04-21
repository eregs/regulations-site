from django.core.urlresolvers import reverse
from django.template.defaultfilters import title

from regulations.generator import api_reader, node_types
from regulations.generator.section_url import SectionUrl
from regulations.generator.versions import fetch_grouped_history
from regulations.views.partial import PartialView
import math

API_PAGE_SIZE = 50
PAGE_SIZE = 10


url_rules = {
    'cfr': 'chrome_search',
    'preamble': 'chrome_search_preamble',
}


class PartialSearch(PartialView):
    """Display search results without any chrome."""
    template_name = 'regulations/search-results.html'

    def add_prev_next(self, current_page, context):
        total = float(context['results']['total_hits']) / PAGE_SIZE
        total = int(math.ceil(total))
        context['current'] = {'page': current_page + 1, 'total': total}

        if current_page > 0:
            context['previous'] = {'length': PAGE_SIZE,
                                   'page': current_page - 1}
        max_this_page = (current_page + 1) * PAGE_SIZE
        remaining = context['results']['total_hits'] - max_this_page
        if remaining > 0:
            context['next'] = {'page': current_page + 1,
                               'length': min(remaining, PAGE_SIZE)}

    def reduce_results(self, results, page):
        """Ignore results found in non-displayable nodes such as the root,
        subparts, etc. Further, the page size returned by the API does not
        match what we display, so we need to reduce the result count
        accordingly. @TODO this is a hack -- we should be able to limit
        results in the request instead"""
        # API page size is API_PAGE_SIZE, but we show only PAGE_SIZE
        page_idx = (page % (API_PAGE_SIZE // PAGE_SIZE)) * PAGE_SIZE
        original_count = len(results['results'])
        is_root = lambda r: len(r['label']) == 1
        is_subpart = lambda r: node_types.type_from_label(r['label']) in (
            node_types.EMPTYPART, node_types.SUBPART, node_types.SUBJGRP)
        results['results'] = [r for r in results['results']
                              if not is_root(r) and not is_subpart(r)]
        num_results_ignored = original_count - len(results['results'])
        results['total_hits'] -= num_results_ignored
        results['results'] = results['results'][page_idx:page_idx + PAGE_SIZE]

    def get_context_data(self, doc_type, **kwargs):
        # We don't want to run the content data of PartialView -- it assumes
        # we will be applying layers
        context = super(PartialView, self).get_context_data(**kwargs)

        context['q'] = self.request.GET.get('q')
        context['version'] = self.request.GET.get('version')
        context['doc_type'] = doc_type

        context['regulation'] = context['label_id'].split('-')[0]
        context['url_rule'] = url_rules[doc_type]

        try:
            page = int(self.request.GET.get('page', '0'))
        except ValueError:
            page = 0

        api_page = page // (API_PAGE_SIZE / PAGE_SIZE)

        context['warnings'] = []
        if not context['q']:
            context['warnings'].append('Please provide a query.')
        if doc_type == 'cfr' and not context['version']:
            context['warnings'].append('Please provide a version.')

        if context['warnings']:
            results = {'results': [], 'total_hits': 0}
        else:
            results = api_reader.ApiReader().search(
                context['q'], context['doc_type'], context['version'],
                context['regulation'], api_page)

        self.reduce_results(results, page)
        section_url = SectionUrl()

        for result in results['results']:
            result['header'] = node_types.label_to_text(result['label'])
            if 'title' in result:
                result['header'] += ' ' + title(result['title'])
            if doc_type == 'cfr':
                result['section_id'] = section_url.view_label_id(
                    result['label'], context['version'])
                result['url'] = section_url.fetch(
                    result['label'], context['version'], sectional=True)
            else:
                result['section_id'] = '-'.join(
                    [result['label'][0], 'preamble'] + result['label'])
                result['url'] = reverse(
                    'chrome_preamble',
                    kwargs={'paragraphs': '/'.join(result['label'][:2])},
                )
        context['results'] = results

        if doc_type == 'cfr':
            for version in fetch_grouped_history(context['regulation']):
                for notice in version['notices']:
                    if notice['document_number'] == context['version']:
                        context['version_by_date'] = notice['effective_on']

        self.add_prev_next(page, context)
        self.final_context = context

        return context
