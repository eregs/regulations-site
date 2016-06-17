# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from unittest import TestCase

from nose.tools import assert_equal, assert_is_none
from mock import patch

from fr_notices import navigation
from regulations.views import preamble  # @todo move this logic


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
                section_id='doc_id-preamble-doc_id-I',
                children=[navigation.NavItem(
                    url='/preamble/doc_id/I#doc_id-I-A',
                    title=navigation.Title('two', 'A', 'two'),
                    section_id='doc_id-preamble-doc_id-I-A'
                )]
            ),
            navigation.NavItem(
                url='/preamble/doc_id/II',
                title=navigation.Title('three', 'II', 'three'),
                section_id='doc_id-preamble-doc_id-II',
            )
        ])

    def test_max_depth(self):
        toc = navigation.make_preamble_nav(self.nodes, max_depth=1)
        self.assertEqual(toc[0].children, [])

    def test_navigation(self):
        toc = navigation.make_preamble_nav(self.nodes)

        nav = preamble.section_navigation(
            toc, [], full_id='doc_id-preamble-doc_id-I')
        assert_equal(nav['next'].section_id, 'doc_id-preamble-doc_id-II')
        assert_is_none(nav['previous'])

        nav = preamble.section_navigation(
            toc, [], full_id='doc_id-preamble-doc_id-II')
        assert_equal(nav['previous'].section_id, 'doc_id-preamble-doc_id-I')
        assert_is_none(nav['next'])


class CFRChangeBuilderTests(TestCase):
    @patch('fr_notices.navigation.fetch_toc')
    @patch('fr_notices.navigation.utils.regulation_meta')
    def test_add_amendment(self, fetch_meta, fetch_toc):
        """Add amendments for two different CFR parts. Verify that the table
        of contents contains only the changed data. Also validate that changes
        to subparts do not include a ToC entry"""
        version_info = {'111': {'left': 'v1', 'right': 'v2'},
                        '222': {'left': 'vold', 'right': 'vnew'}}
        builder = navigation.CFRChangeBuilder('docdoc', version_info)
        fetch_toc.return_value = [
            dict(index=['111', '1'], title='Section 1'),
            dict(index=['111', '1', 'a'], title='1 a'),
            dict(index=['111', '2'], title='Section 2'),
            dict(index=['111', '3'], title='Section 3')]
        fetch_meta.return_value = dict(cfr_title_number='99',
                                       statutory_name='Some title for reg 111')
        builder.add_amendment(dict(cfr_part='111', instruction='1. inst1',
                                   authority='auth1'))
        # subpart change -- doesn't affect ToC
        builder.add_amendment(dict(cfr_part='111', instruction='2. inst2',
                                   changes=[['111-Subpart-A', []]]))
        builder.add_amendment(dict(cfr_part='111', instruction='2. inst2',
                                   # The second element of each pair would be
                                   # non-empty in realistic scenarios
                                   changes=[['111-1', []], ['111-3-b', []]]))

        fetch_toc.return_value = [dict(index=['222', '4'], title='Section 4')]
        fetch_meta.return_value = dict(cfr_title_number='99',
                                       statutory_name='Some title for reg 222')
        # only authority change
        builder.add_amendment(dict(cfr_part='222', instruction='3. inst3',
                                   authority='auth2'))

        self.assertEqual(builder.toc, [
            navigation.ToCPart(
                title='99', part='111', name='Some title for reg 111',
                authority_url='/preamble/docdoc/cfr_changes/111',
                sections=[
                    navigation.ToCSect(
                        section='1', title='Section 1',
                        url='/preamble/docdoc/cfr_changes/111-1',
                        full_id='docdoc-cfr-111-1', part='111'),
                    navigation.ToCSect(
                        section='3', title='Section 3',
                        url='/preamble/docdoc/cfr_changes/111-3',
                        full_id='docdoc-cfr-111-3', part='111')
                ]),
            navigation.ToCPart(
                title='99', part='222', name='Some title for reg 222',
                authority_url='/preamble/docdoc/cfr_changes/222',
                sections=[])])

    def test_navigation(self):
        toc = [
            navigation.ToCPart(
                part='478',
                title='27',
                name='Commerce',
                authority_url='',
                sections=[
                    navigation.ToCSect(
                        full_id='2016_02749-cfr-478-99',
                        url='/preamble/2016_02749/cfr_changes/478-99',
                        title=u'§ 478.99 Certain prohibited',
                        part='478', section='99',
                    ),
                    navigation.ToCSect(
                        full_id='2016_02749-cfr-478-120',
                        url='/preamble/2016_02749/cfr_changes/478-120',
                        title=u'§ 478.120 Firearms',
                        part='478', section='120',
                    ),
                ],
            )
        ]

        nav = preamble.section_navigation([], toc, part='478', section='99')
        assert_equal(nav['next'].section_id, '2016_02749-cfr-478-120')
        assert_equal(nav['previous'].markup_prefix, '27 CFR 478')

        nav = preamble.section_navigation([], toc, part='478', section='120')
        assert_equal(nav['previous'].section_id, '2016_02749-cfr-478-99')
        assert_is_none(nav['next'])

    def test_get_toc_position(self):
        toc = [
            navigation.ToCPart(
                part='478',
                title='27',
                name='Commerce',
                authority_url='',
                sections=[
                    navigation.ToCSect(
                        full_id='2016_02749-cfr-478-99',
                        url='/preamble/2016_02749/cfr_changes/478-99',
                        title=u'§ 478.99 Certain prohibited',
                        part='478', section='99',
                    ),
                    navigation.ToCSect(
                        full_id='2016_02749-cfr-478-120',
                        url='/preamble/2016_02749/cfr_changes/478-120',
                        title=u'§ 478.120 Firearms',
                        part='478', section='120',
                    ),
                ],
            ),
            navigation.ToCPart(
                part='521',
                title='27',
                name='Commerce',
                authority_url='',
                sections=[
                    navigation.ToCSect(
                        full_id='2016_02749-cfr-521-18',
                        url='/preamble/2016_02749/cfr_changes/521-18',
                        title=u'§ 521.18 Something else',
                        part='521', section='18',
                    )
                ],
            )]

        self.assertEqual(0, preamble.get_toc_position(toc,
                         **{'part': '478', 'section': '99'}))
        self.assertEqual(1, preamble.get_toc_position(toc,
                         **{'part': '478', 'section': '120'}))
        self.assertEqual(2, preamble.get_toc_position(toc,
                         **{'part': '521', 'section': '18'}))
        self.assertIsNone(preamble.get_toc_position(toc,
                          **{'part': 'non-existent', 'section': '18'}))
