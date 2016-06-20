# -*- coding: utf-8 -*-

from mock import patch
from unittest import TestCase
from datetime import date, timedelta

from nose.tools import assert_equal, assert_is_none
from django.http import Http404
from django.test import RequestFactory, override_settings

from regulations.generator.layers import diff_applier, layers_applier
from regulations.views import preamble
from regulations.views.preamble import CommentState


class PreambleViewTests(TestCase):
    _mock_preamble = dict(text='1', label=['1'], node_type='', children=[
        dict(text='2', label=['1', 'c'], node_type='', children=[
            dict(text='3', label=['1', 'c', 'i'], node_type='', children=[]),
            dict(text='4', label=['1', 'c', 'x'], node_type='', children=[])
        ]),
        dict(text='5', label=['1', '1'], node_type='', children=[])
    ])

    def test_find_subtree(self):
        """When a node is present in a tree, we should be able to find it.
        When it is not, we should get None"""
        root = self._mock_preamble
        fn = preamble.find_subtree
        self.assertEqual(fn(root, ['1'])['text'], '1')
        self.assertEqual(fn(root, ['1', 'c'])['text'], '2')
        self.assertEqual(fn(root, ['1', 'c', 'i'])['text'], '3')
        self.assertEqual(fn(root, ['1', 'c', 'x'])['text'], '4')
        self.assertEqual(fn(root, ['1', '1'])['text'], '5')
        self.assertIsNone(fn(root, ['2']))
        self.assertIsNone(fn(root, ['1', '2']))
        self.assertIsNone(fn(root, ['1', 'c', 'r']))
        self.assertIsNone(fn(root, ['1', 'c', 'i', 'r']))

    @patch('regulations.views.preamble.CFRChangeToC')
    @patch('regulations.generator.generator.api_reader')
    @patch('regulations.views.preamble.ApiReader')
    def test_get_integration(self, ApiReader, api_reader, CFRChangeToC):
        """Verify that the contexts are built correctly before being sent to
        the template. AJAX/partial=true requests should only get the inner
        context (i.e. no UI-related context)"""
        ApiReader.return_value.preamble.return_value = self._mock_preamble
        api_reader.ApiReader.return_value.layer.return_value = {
            '1-c-x': ['something']
        }
        view = preamble.PreambleView.as_view()

        path = '/preamble/1/c/x?layers=meta'
        response = view(RequestFactory().get(path), paragraphs='1/c/x')
        self.assertEqual(
            response.context_data['sub_context']['node']['text'], '4')
        self.assertEqual(
            response.context_data['sub_context']['node']['children'], [])
        # layer data is present
        self.assertEqual(
            response.context_data['sub_context']['node']['meta'], 'something')
        self.assertEqual(
            response.context_data['preamble_toc'],
            preamble.make_preamble_toc(self._mock_preamble['children']),
        )
        self.assertNotIn('node', response.context_data)

        response = view(RequestFactory().get(path + '&partial=true'),
                        paragraphs='1/c/x')
        self.assertIn('sub_context', response.context_data)
        self.assertEqual(
            response.context_data['sub_context']['node']['text'],
            '4',
        )

        request = RequestFactory().get(
            path, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = view(request, paragraphs='1/c/x')
        self.assertIn('sub_context', response.context_data)
        self.assertEqual(
            response.context_data['sub_context']['node']['text'],
            '4',
        )

    @override_settings(
        PREAMBLE_INTRO={'1': {'meta': {
            'publication_date': '2001-01-01',
            'comments_close': (date.today() + timedelta(days=1)).isoformat()
        }}})
    @patch('regulations.views.preamble.ApiReader')
    def test_comments_open_from_settings(self, ApiReader):
        """
        Mock the PREAMBLE_INTRO data from settings for this test of the
        comments being open.
        """
        _, meta, _ = preamble.notice_data('1')

        assert_equal(meta['comment_state'], CommentState.OPEN)

    def _setup_mock_response(self, ApiReader, **kwargs):
        """Mock the ApiReader response, replacing meta data fields with
        kwargs"""
        ApiReader.return_value.preamble.return_value = self._mock_preamble
        notice = {
            "action": "Proposed rule",
            "agencies": ["Environmental Protection Agency"],
            "cfr_title": 40,
            "cfr_parts": ["300"],
            "comments_close": "2011-09-09",
            "dockets": ["EPA-HQ-SFUND-2010-1086",
                        "FRL-9925-69-OLEM"],
            "primary_agency": "Environmental Protection Agency",
            "title": ("Addition of a Subsurface Intrusion Component to the "
                      "Hazard Ranking System"),
            "publication_date": "2011-02-02",
            "regulatory_id_numbers": ["2050-AG67"],
        }
        notice.update(kwargs)
        ApiReader.return_value.notice.return_value = notice

    @patch('regulations.views.preamble.ApiReader')
    def test_comments_open(self, ApiReader):
        future = date.today() + timedelta(days=10)
        self._setup_mock_response(ApiReader, comments_close=future.isoformat())
        _, meta, _ = preamble.notice_data('1')
        assert_equal(meta['comment_state'], CommentState.OPEN)

    @patch('regulations.views.preamble.ApiReader')
    def test_comments_prepub(self, ApiReader):
        future = date.today() + timedelta(days=10)
        self._setup_mock_response(ApiReader,
                                  publication_date=future.isoformat())
        _, meta, _ = preamble.notice_data('1')
        assert_equal(meta['comment_state'], CommentState.PREPUB)

    @patch('regulations.views.preamble.ApiReader')
    def test_comments_closed(self, ApiReader):
        self._setup_mock_response(ApiReader)
        _, meta, _ = preamble.notice_data('1')
        assert_equal(meta['comment_state'], CommentState.CLOSED)

    @patch('regulations.views.preamble.CFRChangeToC')
    @patch('regulations.generator.generator.api_reader')
    @patch('regulations.views.preamble.ApiReader')
    def test_get_top_level_redirect(self, ApiReader, api_reader, CFRChangeToC):
        ApiReader.return_value.preamble.return_value = self._mock_preamble
        api_reader.ApiReader.return_value.layer.return_value = {
            '1-c-x': ['something']
        }
        view = preamble.PreambleView.as_view()

        path = '/preamble/1'
        response = view(RequestFactory().get(path), paragraphs='1')
        assert_equal(response.status_code, 302)
        assert_equal(response.get('Location'), '/preamble/1/c')

    @patch('regulations.views.preamble.ApiReader')
    def test_get_404(self, ApiReader):
        """When a requested doc is not present, we should return a 404"""
        ApiReader.return_value.preamble.return_value = None
        view = preamble.PreambleView.as_view()
        self.assertRaises(Http404, view,
                          RequestFactory().get('/preamble/1/c/x'),
                          paragraphs='1/c/x')

    @patch('regulations.views.preamble.ApiReader')
    def test_get_subtree_404(self, ApiReader):
        """When a requested _subtree_ is not present, we should 404"""
        ApiReader.return_value.preamble.return_value = self._mock_preamble
        view = preamble.PreambleView.as_view()
        self.assertRaises(Http404, view,
                          RequestFactory().get('/preamble/1/not/here'),
                          paragraphs='1/not/here')

    @patch('regulations.views.preamble.ApiReader')
    def test_notice_data(self, ApiReader):
        """We should try to fetch data corresponding to both the Preamble and
        the Notice"""
        ApiReader.return_value.preamble.return_value = self._mock_preamble
        ApiReader.return_value.notice.return_value = {
            'publication_date': '2002-02-02',
            'comments_close': '2003-03-03',
            'cfr_title': 21, 'cfr_parts': ['123']}

        for doc_id in ('123_456', '123-456'):
            preamble_, meta, notice = preamble.notice_data(doc_id)
            self.assertEqual(preamble_, self._mock_preamble)
            assert_equal(meta['comment_state'], CommentState.CLOSED)
            self.assertEqual(meta['cfr_refs'],
                             [{'title': 21, 'parts': ['123']}])
            self.assertEqual(ApiReader.return_value.preamble.call_args[0][0],
                             '123_456')
            self.assertEqual(ApiReader.return_value.notice.call_args[0][0],
                             '123-456')


class PreambleToCTests(TestCase):

    def setUp(self):
        self.nodes = [
            {
                'title': 'l1',
                'label': ['doc_id', 'I'],
                'children': [
                    {
                        'title': 'l2',
                        'label': ['doc_id', 'I', 'A'],
                    }
                ]
            },
            {
                'title': 'l2',
                'label': ['doc_id', 'II'],
            },
        ]

    def test_preamble_toc(self):
        toc = preamble.make_preamble_toc(self.nodes)
        self.assertEqual(
            toc,
            [
                preamble.PreambleSect(
                    depth=1,
                    title='l1',
                    url='/preamble/doc_id/I',
                    full_id='doc_id-preamble-doc_id-I',
                    children=[
                        preamble.PreambleSect(
                            depth=2,
                            title='l2',
                            url='/preamble/doc_id/I#doc_id-I-A',
                            full_id='doc_id-preamble-doc_id-I-A',
                            children=[],
                        )
                    ]
                ),
                preamble.PreambleSect(
                    depth=1,
                    title='l2',
                    url='/preamble/doc_id/II',
                    full_id='doc_id-preamble-doc_id-II',
                    children=[]
                ),
            ],
        )

    def test_max_depth(self):
        toc = preamble.make_preamble_toc(self.nodes, max_depth=1)
        self.assertEqual(toc[0].children, [])

    def test_navigation(self):
        toc = preamble.make_preamble_toc(self.nodes)

        nav = preamble.section_navigation(
            toc, [], full_id='doc_id-preamble-doc_id-I')
        assert_equal(nav['next'].section_id, 'doc_id-preamble-doc_id-II')
        assert_is_none(nav['previous'])

        nav = preamble.section_navigation(
            toc, [], full_id='doc_id-preamble-doc_id-II')
        assert_equal(nav['previous'].section_id, 'doc_id-preamble-doc_id-I')
        assert_is_none(nav['next'])


class CFRChangesViewTests(TestCase):
    @patch('regulations.views.preamble.ApiReader')
    @patch('regulations.views.preamble.get_appliers')
    def test_new_regtext_changes(self, get_appliers, ApiReader):
        """We can add a whole new section without explosions"""
        amendments = [{'instruction': '3. Add subpart M',
                       'changes': [
                           ['111-Subpart-M', [{'node': {
                               'label': ['111', 'Subpart', 'M'],
                               'title': 'A New Subpart',
                               'child_labels': ['111-42', '111-43',
                                                '111-44', '111-45']}}]],
                           ['111-42', [{'some': 'thing'}]],
                           ['111-43', [{'some': 'thing'}]],
                           ['111-44', [{'some': 'thing'}]],
                           ['111-45', [{'some': 'thing'}]]]},
                      {'instruction': '4. Unrelated'}]
        version_info = {'111': {'left': '234-567', 'right': '8675-309'}}

        # Section did not exist before
        ApiReader.return_value.regulation.return_value = None
        diff = {'111-44': {'op': 'added', 'node': {
            'text': 'New node text', 'node_type': 'regtext',
            'label': ['111', '44']}}}
        get_appliers.return_value = (
            layers_applier.InlineLayersApplier(),
            layers_applier.ParagraphLayersApplier(),
            layers_applier.SearchReplaceLayersApplier(),
            diff_applier.DiffApplier(diff, '111-44'))

        result = preamble.CFRChangesView.regtext_changes_context(
            amendments, version_info, '111-44', '8675-309', 0)
        self.assertEqual(result['instructions'], ['3. Add subpart M'])
        self.assertEqual(result['tree']['marked_up'],
                         '<ins>New node text</ins>')
        self.assertEqual(1, len(result['subparts']))
        subpart_info = result['subparts'][0]
        self.assertEqual('M', subpart_info.letter)
        self.assertEqual('A New Subpart', subpart_info.title)
        self.assertEqual(2, subpart_info.idx)
        self.assertEqual(4, len(subpart_info.urls))
        self.assertIn('111-42', subpart_info.urls[0])
        self.assertIn('111-43', subpart_info.urls[1])
        self.assertIn('111-44', subpart_info.urls[2])
        self.assertIn('111-45', subpart_info.urls[3])


class CFRChangeToCTests(TestCase):
    @patch('regulations.views.preamble.fetch_toc')
    @patch('regulations.views.preamble.utils.regulation_meta')
    def test_add_amendment(self, fetch_meta, fetch_toc):
        """Add amendments for two different CFR parts. Verify that the table
        of contents contains only the changed data. Also validate that changes
        to subparts do not include a ToC entry"""
        version_info = {'111': {'left': 'v1', 'right': 'v2'},
                        '222': {'left': 'vold', 'right': 'vnew'}}
        builder = preamble.CFRChangeToC('docdoc', version_info)
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
            preamble.ToCPart(
                title='99', part='111', name='Some title for reg 111',
                authority_url='/preamble/docdoc/cfr_changes/111',
                sections=[
                    preamble.ToCSect(section='1', title='Section 1',
                                     url='/preamble/docdoc/cfr_changes/111-1',
                                     full_id='docdoc-cfr-111-1', part='111'),
                    preamble.ToCSect(section='3', title='Section 3',
                                     url='/preamble/docdoc/cfr_changes/111-3',
                                     full_id='docdoc-cfr-111-3', part='111')
                ]),
            preamble.ToCPart(
                title='99', part='222', name='Some title for reg 222',
                authority_url='/preamble/docdoc/cfr_changes/222',
                sections=[])])

    def test_navigation(self):
        toc = [
            preamble.ToCPart(
                part='478',
                title='27',
                name='Commerce',
                authority_url='',
                sections=[
                    preamble.ToCSect(
                        full_id='2016_02749-cfr-478-99',
                        url='/preamble/2016_02749/cfr_changes/478-99',
                        title=u'§ 478.99 Certain prohibited',
                        part='478', section='99',
                    ),
                    preamble.ToCSect(
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
            preamble.ToCPart(
                part='478',
                title='27',
                name='Commerce',
                authority_url='',
                sections=[
                    preamble.ToCSect(
                        full_id='2016_02749-cfr-478-99',
                        url='/preamble/2016_02749/cfr_changes/478-99',
                        title=u'§ 478.99 Certain prohibited',
                        part='478', section='99',
                    ),
                    preamble.ToCSect(
                        full_id='2016_02749-cfr-478-120',
                        url='/preamble/2016_02749/cfr_changes/478-120',
                        title=u'§ 478.120 Firearms',
                        part='478', section='120',
                    ),
                ],
            ),
            preamble.ToCPart(
                part='521',
                title='27',
                name='Commerce',
                authority_url='',
                sections=[
                    preamble.ToCSect(
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
