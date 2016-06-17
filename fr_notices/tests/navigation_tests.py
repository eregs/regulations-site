from unittest import TestCase

from nose.tools import assert_equal, assert_is_none

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
