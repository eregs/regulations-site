from copy import deepcopy

from django.core.urlresolvers import reverse

from regulations.generator import api_reader, node_types
from regulations.generator.html_builder import PreambleHTMLBuilder
from regulations.generator.section_url import SectionUrl
from regulations.generator.versions import fetch_grouped_history
from regulations.views.partial import PartialView
import math

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

        context['warnings'] = []
        if not context['q']:
            context['warnings'].append('Please provide a query.')
        if doc_type == 'cfr' and not context['version']:
            context['warnings'].append('Please provide a version.')

        if context['warnings']:
            results = {'results': [], 'total_hits': 0}
        else:
            results = api_reader.ApiReader().search(
                context['q'], context['doc_type'],
                version=context['version'], regulation=context['regulation'],
                page=page, page_size=PAGE_SIZE,
                is_root='false', is_subpart='false',
            )

        if doc_type == 'cfr':
            context['results'] = process_cfr_results(results,
                                                     context['version'])
            for version in fetch_grouped_history(context['regulation']):
                for notice in version['notices']:
                    if notice['document_number'] == context['version']:
                        context['version_by_date'] = notice['effective_on']
        else:
            context['results'] = process_preamble_results(results)

        self.add_prev_next(page, context)

        return context


def add_cfr_headers(result):
    """We always want a title to click, even if the search result doesn't have
    one. We also want to prevent duplication, so we'll only show additional
    levels of headings if they differ."""
    if result.get('title'):
        result['header'] = result['title']
    else:
        result['header'] = node_types.label_to_text(result['label'])
    if result.get('match_title') and result['match_title'] != result['title']:
        result['subheader'] = result['match_title']
    if (result.get('paragraph_title') and
            result['paragraph_title'] != result['match_title']):
        result['subsubheader'] = result['paragraph_title']
    return result


def process_cfr_results(results, version):
    """Modify the results of a search over the CFR by adding a human-readable
    label, appropriate links, and version information"""
    section_url = SectionUrl()
    results = deepcopy(results)
    for result in results['results']:
        add_cfr_headers(result)
        result['section_id'] = section_url.view_label_id(
            result['label'], version)
        result['url'] = section_url.fetch(
            result['label'], version, sectional=True)
    return results


def process_preamble_results(results):
    """Modify the results of a search over a notice preamble by adding a
    human-readable label, appropriate links, etc."""
    results = deepcopy(results)
    for result in results['results']:
        result['header'] = PreambleHTMLBuilder.human_label(result)
        if 'title' in result:
            result['header'] += ' ' + result['title']
        result['section_id'] = '-'.join(
            [result['label'][0], 'preamble'] + result['label'])
        result['url'] = '{}#{}'.format(
            reverse(
                'chrome_preamble',
                kwargs={'paragraphs': '/'.join(result['label'][:2])},
            ),
            '-'.join(result['label']),
        )
    return results
