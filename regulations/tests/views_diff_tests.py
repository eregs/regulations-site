# vim: set fileencoding=utf-8
from unittest import TestCase

from django.test import RequestFactory
from mock import patch

from regulations.views import diff as views_diff


class ChromeSectionDiffViewTests(TestCase):

    def test_extract_sections_subparts(self):
        sub1 = [{'section_id': '8888-1', 'index': ['8888', '1']},
                {'section_id': '8888-3', 'index': ['8888', '3']}]
        sub2 = [{'section_id': '8888-7', 'index': ['8888', '7']}]

        toc = [
            {'section_id': '8888-Subpart-A',
             'index': ['8888', 'Subpart', 'A'],
             'sub_toc': sub1},
            {'section_id': '8888-Subjgrp-IND',
             'index': ['8888', 'Subjgrp', 'IND'],
             'sub_toc': sub2},
            {'section_id': '8888-Interp', 'index': ['8888', 'Interp']},
        ]

        sections = views_diff.extract_sections(toc)
        self.assertEqual(['8888', '1'], sections[0]['index'])
        self.assertEqual(['8888', '3'], sections[1]['index'])
        self.assertEqual(['8888', '7'], sections[2]['index'])
        self.assertEqual(['8888', 'Interp'], sections[3]['index'])

    def test_extract_sections(self):
        toc = [{'section_id': '8888-1', 'index': ['8888', '1']},
               {'section_id': '8888-3', 'index': ['8888', '3']}]
        sections = views_diff.extract_sections(toc)

        self.assertEqual(['8888', '1'], sections[0]['index'])
        self.assertEqual(['8888', '3'], sections[1]['index'])

    def test_diff_toc(self):
        """Integration test."""
        versions = views_diff.Versions('oldold', 'newnew', 'from_ver')
        old_toc = [{'section_id': '8888-1', 'index': ['8888', '1'],
                    'is_section':True},
                   {'section_id': '8888-3', 'index': ['8888', '3'],
                    'is_section':True},
                   {'section_id': '8888-4', 'index': ['8888', '4'],
                    'is_section':True},
                   {'section_id': '8888-A', 'index': ['8888', 'A'],
                    'is_appendix':True},
                   {'section_id': '8888-B', 'index': ['8888', 'B'],
                    'is_appendix':True},
                   {'section_id': '8888-Interp', 'index': ['8888', 'Interp'],
                    'is_supplement':True}]
        diff = {
            '8888-2': {'op': 'added',
                       'node': {'title': u'§ 8888.2', 'label': ['8888', '2']}},
            '8888-C': {'op': 'added',
                       'node': {'title': 'App C', 'label': ['8888', 'C']}},
            '8888-1-a': {'op': 'modified'},
            '8888-B': {'op': 'deleted'},
            '8888-3-b': {'op': 'deleted'},
            '8888-B-1': {'op': 'modified'}
        }

        result = views_diff.diff_toc(versions, old_toc, diff)
        self.assertEqual(8, len(result))
        self.assertTrue('8888-1' in result[0]['url'])
        self.assertTrue('?from_version=from_ver' in result[0]['url'])
        self.assertEqual('8888-1', result[0]['section_id'])
        self.assertEqual('modified', result[0]['op'])
        self.assertTrue('8888-2' in result[1]['url'])
        self.assertTrue('?from_version=from_ver' in result[1]['url'])
        self.assertEqual('8888-2', result[1]['section_id'])
        self.assertEqual('added', result[1]['op'])
        self.assertTrue('8888-3' in result[2]['url'])
        self.assertTrue('?from_version=from_ver' in result[2]['url'])
        self.assertEqual('8888-3', result[2]['section_id'])
        self.assertEqual('modified', result[2]['op'])
        self.assertTrue('8888-4' in result[3]['url'])
        self.assertTrue('?from_version=from_ver' in result[3]['url'])
        self.assertEqual('8888-4', result[3]['section_id'])
        self.assertFalse('op' in result[3])
        self.assertTrue('8888-A' in result[4]['url'])
        self.assertTrue('?from_version=from_ver' in result[4]['url'])
        self.assertEqual('8888-A', result[4]['section_id'])
        self.assertFalse('op' in result[4])
        self.assertTrue('8888-B' in result[5]['url'])
        self.assertTrue('?from_version=from_ver' in result[5]['url'])
        self.assertEqual('8888-B', result[5]['section_id'])
        self.assertEqual('deleted', result[5]['op'])
        self.assertTrue('8888-C' in result[6]['url'])
        self.assertTrue('?from_version=from_ver' in result[6]['url'])
        self.assertEqual('8888-C', result[6]['section_id'])
        self.assertEqual('added', result[6]['op'])
        self.assertTrue('8888-Interp' in result[7]['url'])
        self.assertEqual('8888-Interp', result[7]['section_id'])
        self.assertFalse('op' in result[7])
        for el in result:
            self.assertTrue('oldold', el['url'])
            self.assertTrue('newnew', el['url'])

    def test_interp_headers(self):
        from django.template import loader, Context
        t = loader.get_template('regulations/interp-tree.html')
        context_dict = {'interp': {
            'header': '<ins>My header</ins>', 'section_header': True}}
        response = t.render(Context(context_dict))
        tags_preserved_header = '<h3 tabindex=\"0\"> <ins>My header</ins></h3>'
        self.assertTrue(tags_preserved_header in response)

    @patch('regulations.views.diff.fetch_toc')
    @patch('regulations.views.diff.SectionUrl')
    def test_add_main_content(self, SectionUrl, fetch_toc):
        fetch_toc.return_value = [
            {'index': ['1111', '222'], 'is_section': True},
            {'index': ['1111', 'B'], 'is_appendix': True},
            {'index': ['1111', 'Interp'], 'is_supplement': True,
             'sub_toc': [
                 {'index': ['1111', 'Interp', 'h1']},
                 {'index': ['1111', 'Subpart', 'Interp']},
                 {'index': ['1111', 'A', 'Interp']}]}]
        context = {
            'main_content_context': {'newer_version': '1', 'TOC': 'toc'},
            'label_id': '111-222',
            'version': '2'}
        request = RequestFactory().get('?new_version=1')
        csdv = views_diff.ChromeSectionDiffView()
        csdv.request = request

        csdv.add_diff_content(context)
        self.assertEqual(context['from_version'], '2')
        self.assertEqual(context['left_version'], '2')
        self.assertEqual(context['right_version'], '1')
        self.assertEqual(context['TOC'], 'toc')
        self.assertTrue('first_subterp' in context)
        self.assertEqual(['1111', 'Interp', 'h1'],
                         context['first_subterp']['index'])
        self.assertTrue('url' in context['first_subterp'])


class PartialSectionDiffViewTests(TestCase):
    def setUp(self):
        self.versions = views_diff.Versions('old', 'new', 'from')
        self.toc = [{'section_id': '9898-1'}, {'section_id': '9898-5'},
                    {'section_id': '9898-A'}, {'section_id': '9898-Interp'}]
        self.view = views_diff.PartialSectionDiffView()

    def assert_url_contains_versions(self, url, section_id):
        """The provided url should contain the appropriate strings for the
        old, new, and return_to urls"""
        from_version = '?from_version=' + self.versions.return_to
        self.assertTrue(self.versions.older in url)
        self.assertTrue(self.versions.newer in url)
        self.assertTrue(from_version in url)
        self.assertTrue(section_id in url)

    def assert_correct_nav(self, section_id, prev, following):
        """Verify that the generated nav contains the appropriate url entries
        for prev and next"""
        nav = self.view.footer_nav(section_id, self.toc, self.versions)
        self.assertEqual(nav['page_type'], 'diff')
        if prev:
            self.assert_url_contains_versions(nav['previous']['url'], prev)
        else:
            self.assertFalse('previous' in nav)

        if following:
            self.assert_url_contains_versions(nav['next']['url'], following)
        else:
            self.assertFalse('next' in nav)

    def test_footer_nav(self):
        self.assert_correct_nav('9898-2', prev=None, following=None)
        self.assert_correct_nav('9898-1', prev=None, following='9898-5')
        self.assert_correct_nav('9898-5', prev='9898-1', following='9898-A')
        self.assert_correct_nav('9898-A', prev='9898-5',
                                following='9898-Interp')
        self.assert_correct_nav('9898-Interp', prev='9898-A', following=None)
