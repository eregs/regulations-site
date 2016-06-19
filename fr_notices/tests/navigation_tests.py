# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from unittest import TestCase

from nose.tools import assert_equal, assert_is_none
from mock import patch

from fr_notices import navigation


class PreambleToCTests(TestCase):
    def setUp(self):
        self.nodes = [{
            'title': 'one',
            'label': ['doc_id', 'I'],
            'children': [{
                'title': 'two',
                'label': ['doc_id', 'I', 'A'],
            }]
        }, {
            'title': 'three',
            'label': ['doc_id', 'II'],
        }]

    def test_preamble_toc(self):
        toc = navigation.make_preamble_nav(self.nodes)
        self.assertEqual(toc, [
            navigation.NavItem(
                url='/preamble/doc_id/I',
                title=navigation.Title('one', 'I', 'one'),
                markup_id='doc_id-preamble-doc_id-I',
                children=[navigation.NavItem(
                    url='/preamble/doc_id/I#doc_id-I-A',
                    title=navigation.Title('two', 'A', 'two'),
                    markup_id='doc_id-preamble-doc_id-I-A',
                )]
            ),
            navigation.NavItem(
                url='/preamble/doc_id/II',
                title=navigation.Title('three', 'II', 'three'),
                markup_id='doc_id-preamble-doc_id-II',
            )
        ])

    def test_max_depth(self):
        toc = navigation.make_preamble_nav(self.nodes, max_depth=1)
        self.assertEqual(toc[0].children, [])

    def test_footer(self):
        toc = navigation.make_preamble_nav(self.nodes)

        nav = navigation.footer(toc, [], 'doc_id-preamble-doc_id-I')
        assert_equal(nav['next'].section_id, 'doc_id-preamble-doc_id-II')
        assert_is_none(nav['previous'])

        nav = navigation.footer(toc, [], 'doc_id-preamble-doc_id-II')
        assert_equal(nav['previous'].section_id, 'doc_id-preamble-doc_id-I')
        assert_is_none(nav['next'])


class CFRChangeBuilderTests(TestCase):
    @patch('fr_notices.navigation.fetch_toc')
    @patch('fr_notices.navigation.utils.regulation_meta')
    def test_make_cfr_change_nav(self, fetch_meta, fetch_toc):
        """Add amendments for two different CFR parts. Verify that the table
        of contents contains only the changed data. Also validate that changes
        to subparts do not include a ToC entry"""
        version_info = {'111': {'left': 'v1', 'right': 'v2'},
                        '222': {'left': 'vold', 'right': 'vnew'}}
        fetch_toc.return_value = [
            dict(index=['111', '1'], title='§ 111.1 Something'),
            dict(index=['111', '1', 'a'], title='1 a'),
            dict(index=['111', '2'], title='§ 111.2 Else Here'),
            dict(index=['111', '3'], title='Unparsable'),
            # Realistically we wouldn't have these together, but it makes
            # mocking these results easier
            dict(index=['222', '4'], title='Section 4')
        ]
        fetch_meta.return_value = dict(cfr_title_number='99',
                                       statutory_name='Some name')
        toc = navigation.make_cfr_change_nav('docdoc', version_info, [
            dict(cfr_part='111', instruction='1. inst1', authority='auth1'),
            # subpart change -- doesn't affect ToC
            dict(cfr_part='111', instruction='2. inst2',
                 changes=[['111-Subpart-A', []]]),
            dict(cfr_part='111', instruction='2. inst2',
                 # The second element of each pair would be
                 # non-empty in realistic scenarios
                 changes=[['111-1', []], ['111-3-b', []]]),
            # only authority change
            dict(cfr_part='222', instruction='3. inst3', authority='auth2')
        ])

        self.assertEqual(toc, [
            navigation.NavItem(
                url='/preamble/docdoc/cfr_changes/111',
                title=navigation.Title('Authority', '99 CFR 111', 'Authority'),
                markup_id='docdoc-cfr-111',
                category='99 CFR 111',
                section_id=''),
            navigation.NavItem(
                url='/preamble/docdoc/cfr_changes/111-1',
                title=navigation.Title(
                    '§ 111.1 Something', '§ 111.1', 'Something'),
                markup_id='docdoc-cfr-111-1',
                category='99 CFR 111'),
            navigation.NavItem(
                url='/preamble/docdoc/cfr_changes/111-3',
                title=navigation.Title('Unparsable', 'Unparsable'),
                markup_id='docdoc-cfr-111-3',
                category='99 CFR 111'),
            navigation.NavItem(
                url='/preamble/docdoc/cfr_changes/222',
                title=navigation.Title('Authority', '99 CFR 222', 'Authority'),
                markup_id='docdoc-cfr-222',
                category='99 CFR 222',
                section_id='')
        ])

    def test_footer(self):
        toc = [
            navigation.NavItem(
                url='/preamble/2016_02749/cfr_changes/478',
                title=navigation.Title('Authority', '27 CFR 478', 'Authority'),
                markup_id='2016_02749-cfr-478',
                category='27 CFR 478'),
            navigation.NavItem(
                url='/preamble/2016_02749/cfr_changes/478-99',
                title=navigation.Title(
                    '§ 478.99 Certain', '§ 478.99', 'Certain'),
                markup_id='2016_02749-cfr-478-99',
                category='27 CFR 478'),
            navigation.NavItem(
                url='/preamble/2016_02749/cfr_changes/478-120',
                title=navigation.Title(
                    '§ 478.120 Firearms', '§ 478.120', 'Firearms'),
                markup_id='2016_02749-cfr-478-120',
                category='27 CFR 478')
        ]

        nav = navigation.footer([], toc, '2016_02749-cfr-478')
        assert_is_none(nav['previous'])
        assert_equal(nav['next'].section_id, '2016_02749-cfr-478-99')

        nav = navigation.footer([], toc, '2016_02749-cfr-478-99')
        assert_equal(nav['previous'].section_id, '2016_02749-cfr-478')
        assert_equal(nav['next'].section_id, '2016_02749-cfr-478-120')

        nav = navigation.footer([], toc, '2016_02749-cfr-478-120')
        assert_equal(nav['previous'].section_id, '2016_02749-cfr-478-99')
        assert_is_none(nav['next'])
