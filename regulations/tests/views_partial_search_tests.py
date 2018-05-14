# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import date

from mock import Mock

from regulations.generator import section_url
from regulations.generator.versions import Timeline
from regulations.views import partial_search


def test_get(client, monkeypatch):
    monkeypatch.setattr(partial_search, 'api_reader', Mock())
    monkeypatch.setattr(partial_search, 'fetch_grouped_history', Mock())
    partial_search.api_reader.ApiReader.return_value.search.return_value = {
        'total_hits': 3333,
        'results': [
            {'label': ['111', '22'], 'text': 'tttt', 'version': 'vvv',
             'title':"Consumer's"},
            {'label': ['111', '24', 'a'], 'text': 'o', 'version': 'vvv'},
            {'label': ['111', '25'], 'text': 'more', 'version': 'vvv'}
        ]
    }
    partial_search.fetch_grouped_history.return_value = [
        {'notices': [{'document_number': 'bbb',
                      'effective_on': date(2012, 12, 12)}]},
        {'notices': [{'document_number': 'ccc',
                      'effective_on': date(2001, 1, 1)},
                     {'document_number': 'vvv',
                      'effective_on': date(2003, 4, 5)}],
         'timeline': Timeline.past}
    ]
    response = client.get('/partial/search/111?version=vvv&q=none').content
    assert b'111-22' in response
    assert b'111-24-a' in response
    assert b'111.24(a)' in response
    assert b'111-25' in response
    assert b'111.25' in response
    assert b'3333' in response
    assert b'Consumer&#39;s' in response


def test_root_info(client, monkeypatch):
    monkeypatch.setattr(partial_search, 'api_reader', Mock())
    monkeypatch.setattr(partial_search, 'fetch_grouped_history', Mock())
    partial_search.api_reader.ApiReader.return_value.search.return_value = {
        'total_hits': 2,
        'results': [
            {'label': ['444', '22'], 'text': 'tttt', 'version': 'vvv',
             'title':"consumer's"},
            {'label': ['444', '24', 'a'], 'text': 'o', 'version': 'vvv'},
        ]
    }
    partial_search.fetch_grouped_history.return_value = [
        {'notices': [{'document_number': 'bbb',
                      'effective_on': date(2012, 12, 12)}]},
        {'notices': [{'document_number': 'ccc',
                      'effective_on': date(2001, 1, 1)},
                     {'document_number': 'vvv',
                      'effective_on': date(2003, 4, 5)}],
         'timeline': Timeline.past}
    ]
    response = client.get('/partial/search/444?version=vvv&q=none').content
    assert b'2 results' in response


def test_subinterp(client, monkeypatch):
    monkeypatch.setattr(partial_search, 'api_reader', Mock())
    monkeypatch.setattr(partial_search, 'fetch_grouped_history', Mock())
    monkeypatch.setattr(section_url, 'fetch_toc', Mock())

    section_url.fetch_toc.return_value = [
        {'index': ['444', 'Subpart', 'B'], 'is_subpart': True,
         'section_id': '444-Subpart-B', 'sub_toc': [
            {'index': ['444', '22'], 'section_id': '444-22',
             'is_section': True}]},
        {'index': ['444', 'Interp'], 'section_id': '444-Interp',
         'sub_toc': [
            {'index': ['444', 'Interp', 'h1'],
             'section_id': '444-Interp-h1'},
            {'index': ['444', 'Subpart', 'B', 'Interp'],
             'section_id': '444-Subpart-B-Interp'}]}
    ]
    partial_search.api_reader.ApiReader.return_value.search.return_value = {
        'total_hits': 3,
        'results': [
            {'label': ['444', '22', 'Interp'], 'text': 'tttt',
             'version': 'vvv', 'title':"consumer's"},
            {'label': ['444', 'Interp', 'h1', 'p5'], 'text': 'o',
             'version': 'vvv'}
        ]
    }
    partial_search.fetch_grouped_history.return_value = [
        {'notices': [{'document_number': 'bbb',
                      'effective_on': date(2012, 12, 12)}]},
        {'notices': [{'document_number': 'ccc',
                      'effective_on': date(2001, 1, 1)},
                     {'document_number': 'vvv',
                      'effective_on': date(2003, 4, 5)}],
         'timeline': Timeline.past}
    ]

    response = client.get('/partial/search/444?version=vvv&q=other').content
    assert b'444-Subpart-B-Interp' in response
    assert b'444-Interp-h1' in response


def test_no_results(client, monkeypatch):
    monkeypatch.setattr(partial_search, 'api_reader', Mock())
    monkeypatch.setattr(partial_search, 'fetch_grouped_history', Mock())
    partial_search.api_reader.ApiReader.return_value.search.return_value = {
        'total_hits': 0,
        'results': []
    }
    partial_search.fetch_grouped_history.return_value = [
        {'notices': [{'document_number': 'bbb',
                      'effective_on': date(2012, 12, 12)}]},
        {'notices': [{'document_number': 'ccc',
                      'effective_on': date(2001, 1, 1)},
                     {'document_number': 'vvv',
                      'effective_on': date(2003, 4, 5)}],
         'timeline': Timeline.past}
    ]
    response = client.get('/partial/search/121?version=vvv&q=none').content
    assert b'4/5/2003' in response


def test_null_params(client, monkeypatch):
    monkeypatch.setattr(partial_search, 'fetch_grouped_history',
                        Mock(return_value=[]))

    response = client.get('/partial/search/111?version=vvv').content
    assert b'provide a query' in response

    response = client.get('/partial/search/111?q=vvv').content
    assert b'provide a version' in response


def test_preamble_search(client, monkeypatch):
    monkeypatch.setattr(partial_search, 'api_reader', Mock())
    partial_search.api_reader.ApiReader.return_value.search.return_value = {
        'total_hits': 3333,
        'results': [
            {'label': ['111_22', 'I', 'A'], 'text': 'tttt',
             'title': 'A. Something'},
            {'label': ['111_22', 'I', 'p1'], 'text': 'eee'}
        ]
    }

    response = client.get('/partial/search/preamble/111?q=none').content
    assert b'111_22-I-A' in response
    assert b'111_22-I-p1' in response
    assert b'tttt' in response
    assert b'eee' in response
    assert b'A. Something' in response
    assert b'Section I.A' in response


def test_page_size(client, monkeypatch):
    """Page size should be passed along to the API"""
    monkeypatch.setattr(partial_search, 'api_reader', Mock())
    search = partial_search.api_reader.ApiReader.return_value.search
    search.return_value = {'total_hits': 0, 'results': []}

    client.get('/partial/search/preamble/111?q=none')

    assert search.call_args[1]['page_size'] == 10


def test_add_prev_next():
    view = partial_search.PartialSearch()
    context = {'results': {'total_hits': 77}}
    view.add_prev_next(0, context)
    assert 'previous' not in context
    assert context['next'] == {'page': 1, 'length': 10}

    del context['next']
    view.add_prev_next(5, context)
    assert context['previous'] == {'page': 4, 'length': 10}
    assert context['next'] == {'page': 6, 'length': 10}

    del context['previous']
    del context['next']
    view.add_prev_next(6, context)
    assert context['previous'] == {'page': 5, 'length': 10}
    assert context['next'] == {'page': 7, 'length': 7}

    del context['previous']
    del context['next']
    view.add_prev_next(7, context)
    assert context['previous'] == {'page': 6, 'length': 10}
    assert 'next' not in context


def test_add_cfr_headers_no_title():
    """If no title is present in the result data, we construct one based on
    its label."""
    result = partial_search.add_cfr_headers({'label': ['111', '22', 'c', '4']})
    assert result['header'] == '111.22(c)(4)'


def test_add_cfr_headers_section():
    """If all of the titles are the same (as is the case when a section's
    intro text matches our search), we don't need to repeat them."""
    result = partial_search.add_cfr_headers({'title': 'Section 22',
                                             'match_title': 'Section 22',
                                             'paragraph_title': 'Section 22'})
    assert result['header'] == 'Section 22'
    assert 'subheader' not in result
    assert 'subsubheader' not in result


def test_add_cfr_headers_three_levels():
    """If the three levels of title are different, we expect them in our
    results."""
    result = partial_search.add_cfr_headers({
        'title': 'Section 22',
        'match_title': 'A matching heading',
        'paragraph_title': 'A title for text',
    })
    assert result['header'] == 'Section 22'
    assert result['subheader'] == 'A matching heading'
    assert result['subsubheader'] == 'A title for text'
