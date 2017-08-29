from datetime import date

import pytest
from django.http import HttpResponseGone
from mock import call, Mock

from regulations.generator.versions import Timeline
from regulations.views import chrome, error_handling


def test_version_span():
    history = [
        {'by_date': date(2009, 9, 9), 'timeline': Timeline.future},
        {'by_date': date(2008, 8, 8), 'timeline': Timeline.present},
        {'by_date': date(2007, 7, 7), 'timeline': Timeline.past},
    ]
    result = chrome.version_span(history, date(2010, 10, 10))
    assert result == chrome.VersionSpan(date(2009, 9, 9), None,
                                        Timeline.future)

    result = chrome.version_span(history, date(2009, 9, 8))
    assert result == chrome.VersionSpan(date(2008, 8, 8), date(2009, 9, 9),
                                        Timeline.present)

    result = chrome.version_span(history, date(2007, 8, 9))
    assert result == chrome.VersionSpan(date(2007, 7, 7), date(2008, 8, 8),
                                        Timeline.past)


def test_chrome_404(monkeypatch, rf):
    """Test that the response of the outer view is that of the inner when
    there's an error"""
    monkeypatch.setattr(chrome.ChromeView, 'set_chrome_context', Mock())
    monkeypatch.setattr(chrome, 'generator', Mock())
    monkeypatch.setattr(error_handling, 'api_reader', Mock())

    regversions = error_handling.api_reader.ApiReader.return_value.regversions
    regversions.return_value = None
    chrome.generator.get_tree_paragraph.return_value = {}
    chrome.ChromeView.set_chrome_context.return_value = None

    class InnerView(chrome.TemplateView):
        def get(self, request, *args, **kwargs):
            return HttpResponseGone()

    class FakeView(chrome.ChromeView):
        partial_class = InnerView

    view = FakeView()
    view.request = rf.get('/')
    response = view.get(view.request, label_id='lab', version='ver')
    assert response.status_code == 404


def test_chrome_error_propagation(monkeypatch, rf):
    """While we don't rely on this sort of propagation for the main content
    (much), test it in the sidebar"""
    monkeypatch.setattr(chrome, 'error_handling', Mock())
    monkeypatch.setattr(chrome, 'generator', Mock())
    monkeypatch.setattr(chrome, 'SideBarView', Mock())
    chrome.SideBarView.as_view.return_value.return_value = HttpResponseGone()

    class FakeView(chrome.ChromeView):
        def add_main_content(self, context):
            pass

        def set_chrome_context(self, context, reg_part, version):
            pass

    view = FakeView()
    view.request = rf.get('/')
    response = view.get(view.request, label_id='lab', version='ver')
    assert response.status_code == 410


def test_chrome_get_404(client, monkeypatch):
    monkeypatch.setattr(chrome, 'generator', Mock())
    chrome.generator.get_regulation.return_value = None
    response = client.get('/regulation/111/222')
    assert response.status_code == 404


def test_chrome_get_404_tree(client, monkeypatch):
    monkeypatch.setattr(chrome, 'generator', Mock())
    chrome.generator.get_regulation.return_value = {'regulation': 'tree'}
    chrome.generator.get_tree_paragraph.return_value = None
    response = client.get('/regulation/111/222')
    assert response.status_code == 404


def test_chrome_diff_redirect_label_regulation():
    """If viewing a full regulation, the redirect for diffs should point to
    the first section"""
    view = chrome.ChromeView()
    toc = [{'section_id': '199-Subpart-A',
            'sub_toc': [{'section_id': '199-4'}, {'section_id': '199-6'}]},
           {'section_id': '199-Subpart-B',
            'sub_toc': [{'section_id': '199-8'}, {'section_id': '199-9'}]}]
    assert view.diff_redirect_label('199', toc) == '199-4'


@pytest.mark.parametrize('label, expected', (
    ('199-4-b', '199-4'),
    ('199-4-b-3', '199-4'),
    ('199-A', '199-A'),
    ('199-A-14B', '199-A'),
    ('199-Interp', '199-Interp'),
    ('199-Interp-h1', '199-Interp'),
    ('199-12-Interp-2', '199-Interp'),
))
def test_chrome_diff_redirect_label_paragraph(label, expected):
    """If viewing a single paragraph, the redirect for diffs should point to
    that paragraph's section. Similarly, all diffs for interpretations should
    point to the root interpretation"""
    view = chrome.ChromeView()
    assert view.diff_redirect_label(label, []) == expected


@pytest.mark.parametrize('label', (
    '199-Subpart-Interp', '199-Subpart-A-Interp', '199-Appendices-Interp'))
def test_subterp_diff_redirect_label(label):
    view = chrome.ChromeSubterpView()
    assert '199-Interp' == view.diff_redirect_label(label, None)


def test_subterp_check_tree(monkeypatch):
    monkeypatch.setattr(chrome, 'generator', Mock())
    monkeypatch.setattr(chrome, 'filter_by_subterp', Mock())
    chrome.generator.get_tree_paragraph.return_value = None

    view = chrome.ChromeSubterpView()
    with pytest.raises(chrome.error_handling.MissingSectionException):
        view.check_tree({'version': 'vvvv', 'label_id': 'llll'})

    chrome.generator.get_tree_paragraph.return_value = {'children': []}
    chrome.filter_by_subterp.return_value = []
    with pytest.raises(chrome.error_handling.MissingSectionException):
        view.check_tree({'version': 'vvvv', 'label_id': 'llll'})

    chrome.filter_by_subterp.return_value = ["something"]
    # No exception
    view.check_tree({'version': 'vvvv', 'label_id': 'llll'})


def test_chrome_search_version_present(monkeypatch, rf):
    """If a version is in the request, we use it to derive the label_id."""
    monkeypatch.setattr(chrome, 'utils', Mock())
    chrome.utils.first_section.return_value = '111-22'

    view = chrome.ChromeSearchView()
    view.request = rf.get('/?version=some-version')
    result = view.fill_kwargs({'label_id': '111'})

    assert result == {
        'version': 'some-version',
        'skip_count': True,
        'label_id': '111-22',
    }
    assert chrome.utils.first_section.call_args == call('111', 'some-version')


def test_chome_search_missing_version(monkeypatch, rf):
    """A missing version shouldn't cause the results page to explode"""
    monkeypatch.setattr(chrome, 'utils', Mock())
    monkeypatch.setattr(chrome, 'get_versions', Mock())
    chrome.get_versions.return_value = (
        {'version': 'current-version'}, {'version': 'next-version'})
    chrome.utils.first_section.return_value = '222-33'

    view = chrome.ChromeSearchView()
    view.request = rf.get('/')
    result = view.fill_kwargs({'label_id': '222'})

    assert result == {
        'version': 'current-version',
        'skip_count': True,
        'label_id': '222-33',
    }
    assert chrome.get_versions.call_args == call('222')
    assert chrome.utils.first_section.call_args == call('222',
                                                        'current-version')
