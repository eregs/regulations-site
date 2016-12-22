# -*- coding: utf-8 -*-
from unittest import TestCase

from regulations.generator.html_builder import (
    CFRChangeHTMLBuilder, CFRHTMLBuilder, HTMLBuilder, PreambleHTMLBuilder)
from regulations.generator.layers.diff_applier import DiffApplier
from regulations.generator.layers.internal_citation import (
    InternalCitationLayer)
from regulations.generator.node_types import REGTEXT, APPENDIX, INTERP
from regulations.generator.layers import diff_applier


class HTMLBuilderTest(TestCase):
    def test_process_node_header(self):
        builder = HTMLBuilder()
        node = {'text': '', 'children': [], 'label': ['99', '22'],
                'node_type': REGTEXT}
        builder.process_node(node)
        self.assertFalse('header' in node)

        node = {'text': '', 'children': [], 'label': ['99', '22'],
                'title': 'Some Title', 'node_type': REGTEXT}
        builder.process_node(node)
        self.assertTrue('header' in node)
        self.assertEqual('Some Title', node['header'])

        node = {'text': '', 'children': [], 'label': ['99', '22'],
                'title': u'§ 22.1 Title', 'node_type': REGTEXT}
        builder.process_node(node)
        self.assertTrue('header' in node)

    def test_process_node_title_diff(self):
        builder = HTMLBuilder()
        diff = {'204': {'title': [('delete', 0, 2), ('insert', 4, 'AAC')],
                        'text':  [('delete', 0, 2), ('insert', 4, 'AAB')],
                        'op': ''}}
        da = diff_applier.DiffApplier(diff, None)
        node = {
            "label_id": "204",
            "title": "abcd",
            'node_type': APPENDIX
        }
        builder.diff_applier = da
        builder.process_node_title(node)
        self.assertEqual('<del>ab</del>cd<ins>AAC</ins>', node['header'])

    def test_node_title_no_diff(self):
        builder = HTMLBuilder()
        node = {
            "label_id": "204",
            "title": "abcd",
            'node_type': APPENDIX
        }
        builder.process_node_title(node)
        self.assertTrue('header' in node)
        self.assertEqual(node['title'], 'abcd')

    def test_is_collapsed(self):
        for label, text in ((['111', '22', 'a'], '(a) '),
                            (['111', '22', 'xx'], ' (xx) '),
                            (['111', '22', 'a', '5'], '(5)')):
            node = {'label': label, 'text': text}
            self.assertTrue(HTMLBuilder.is_collapsed(node))

        for label, text in ((['111', '22', 'a'], '(b) '),
                            (['111', '22', ''], '(a) Some text'),
                            (['111', '22', 'a'], '  ')):
            node = {'label': label, 'text': text}
            self.assertFalse(HTMLBuilder.is_collapsed(node))

    def test_human_label(self):
        self.assertEqual(
            '111', HTMLBuilder.human_label({'label': ['111']}))
        self.assertEqual(
            '111-22-33-aa',
            HTMLBuilder.human_label({'label': ['111', '22', '33', 'aa']}))


class CFRHTMLBuilderTest(TestCase):
    def test_list_level_interpretations(self):
        builder = CFRHTMLBuilder()

        parts = ['101', '12', 'a', 'Interp', '1']
        node_type = INTERP

        result = builder.list_level(parts, node_type)
        self.assertEquals(result, 1)

        parts.append('j')
        result = builder.list_level(parts, node_type)
        self.assertEquals(result, 2)

        parts.append('B')
        result = builder.list_level(parts, node_type)
        self.assertEquals(result, 3)

    def test_list_level_appendices(self):
        builder = CFRHTMLBuilder()

        parts = ['101', 'A', '1', 'a']
        node_type = APPENDIX

        result = builder.list_level(parts, node_type)
        self.assertEquals(result, 1)

        parts.append('2')
        result = builder.list_level(parts, node_type)
        self.assertEquals(result, 2)

        parts.append('k')
        result = builder.list_level(parts, node_type)
        self.assertEquals(result, 3)

        parts.append('B')
        result = builder.list_level(parts, node_type)
        self.assertEquals(result, 4)

    def test_list_level_regulations(self):
        builder = CFRHTMLBuilder()

        parts = ['101', '1', 'a']
        node_type = REGTEXT

        result = builder.list_level(parts, node_type)
        self.assertEquals(result, 1)

        parts.append('2')
        result = builder.list_level(parts, node_type)
        self.assertEquals(result, 2)

        parts.append('k')
        result = builder.list_level(parts, node_type)
        self.assertEquals(result, 3)

        parts.append('B')
        result = builder.list_level(parts, node_type)
        self.assertEquals(result, 4)

    def test_list_level_regulations_no_level(self):
        builder = CFRHTMLBuilder()

        parts = ['101', '1']
        node_type = REGTEXT

        result = builder.list_level(parts, node_type)
        self.assertEquals(result, 0)

    def test_no_section_sign(self):
        text = CFRHTMLBuilder.section_space(' abc')
        self.assertEquals(text, ' abc')

    def test_modify_interp_node(self):
        node = {
            'node_type': INTERP,
            'label': ['872', '22', 'Interp'],
            'children': [{'label': ['872', '22', 'Interp', '1']},
                         {'label': ['872', '22', 'a', 'Interp']},
                         {'label': ['872', '22', 'b', 'Interp']}]
        }
        builder = CFRHTMLBuilder()
        builder.modify_interp_node(node)
        self.assertTrue(node['section_header'])
        self.assertEqual(node['header_children'],
                         [{'label': ['872', '22', 'a', 'Interp']},
                          {'label': ['872', '22', 'b', 'Interp']}])
        self.assertEqual(node['par_children'],
                         [{'label': ['872', '22', 'Interp', '1']}])

        node['label'] = ['872', '222', 'a', 'Interp']
        builder.modify_interp_node(node)
        self.assertFalse(node['section_header'])

    def test_modify_interp_node_header(self):
        node = {
            'children': [],
            'header': 'This interprets 22(a), a paragraph',
            'label': ['872', '22', 'a', 'Interp'],
            'node_type': INTERP,
        }
        icl = InternalCitationLayer(None)
        icl.sectional = True
        builder = CFRHTMLBuilder([icl])

        builder.modify_interp_node(node)
        self.assertEqual('This interprets '
                         + icl.render_url(['872', '22', 'a'], '22(a)')
                         + ', a paragraph', node['header_markup'])

        node['label'] = ['872', '22']
        builder.modify_interp_node(node)
        self.assertEqual(node['header'], node['header_markup'])

    def test_process_node_title_section_space_diff(self):
        """" Diffs and sections spaces need to place nicely together. """
        builder = CFRHTMLBuilder()
        diff = {'204': {'title': [('delete', 7, 9), ('insert', 10, 'AAC')],
                        'text':  [('delete', 0, 2), ('insert', 4, 'AAB')],
                        'op': ''}}
        da = diff_applier.DiffApplier(diff, None)
        node = {
            "label_id": u"204",
            "title": u"§ 101.6 abcd",
            'node_type': APPENDIX
        }
        builder.diff_applier = da
        builder.process_node_title(node)
        self.assertEqual(
            u'§&nbsp;101.6<del> a</del>b<ins>AAC</ins>cd', node['header'])

    def test_human_label(self):
        self.assertEqual(
            'Regulation 111', CFRHTMLBuilder.human_label({'label': ['111']}))
        self.assertEqual(
            u'§ 111.22(f)',
            CFRHTMLBuilder.human_label({'label': ['111', '22', 'f']}))


class PreambleHTMLBuilderTest(TestCase):
    def setUp(self):
        self.builder = PreambleHTMLBuilder()

    def test_human_label(self):
        self.assertEqual(
            'FR #111_22',
            PreambleHTMLBuilder.human_label({'label': ['111_22']}))
        self.assertEqual(
            'Section III.A.ii.4',
            PreambleHTMLBuilder.human_label({
                'label': ['111_22', 'III', 'A', 'ii', '4'],
                'indexes': [2, 0, 1, 3],
            }),
        )
        self.assertEqual(
            'Section III.A.ii.4 Paragraph 3.5',
            PreambleHTMLBuilder.human_label({
                'label': ['111_22', 'III', 'A', 'ii', '4', 'p3', 'p7'],
                'indexes': [2, 0, 1, 3, 2, 4]
            }),
        )

    def test_accepts_comment(self):
        """All of the preamble can be commented on. Some of it is called
        out"""
        node = {'label': ['ABCD_123', 'II', 'B', 'p4'], 'text': 'Something',
                'node_type': 'preamble', 'children': []}
        self.builder.process_node(node)
        self.assertTrue(node.get('accepts_comments'))
        self.assertFalse(node.get('comments_calledout'))

        node = {'title': 'B. Has a title', 'label': ['ABCD_123', 'II', 'B'],
                'text': 'Something', 'node_type': 'preamble', 'children': []}
        self.builder.process_node(node)
        self.assertTrue(node.get('accepts_comments'))
        self.assertTrue(node.get('comments_calledout'))


class CFRChangeHTMLBuilderTests(TestCase):
    def setUp(self):
        diffs = DiffApplier({'111-22-a': {'op': 'deleted'}}, '111-22')
        self.builder = CFRChangeHTMLBuilder([], diffs)

    def test_accepts_comment(self):
        """We can only comment on changed paragraphs"""
        node = {'label': ['111', '21', 'a'], 'text': 'Something',
                'node_type': 'regtext', 'children': []}
        self.builder.process_node(node)
        self.assertFalse(node.get('accepts_comments'))
        self.assertEqual(node.get('stars_collapse'), 'full')

        node['label'] = ['111', '22']
        self.builder.process_node(node)
        self.assertFalse(node.get('accepts_comments'))
        self.assertEqual(node.get('stars_collapse'), 'inline')

        node['label'] = ['111', '22', 'a', '5']
        self.builder.process_node(node)
        self.assertFalse(node.get('accepts_comments'))
        self.assertEqual(node.get('stars_collapse'), 'full')

        node['label'] = ['111', '22', 'a']
        self.builder.process_node(node)
        self.assertTrue(node.get('accepts_comments'))
        self.assertEqual(node.get('stars_collapse'), 'none')

    def test_preprocess(self):
        diffs = DiffApplier({'111-22-a': {'op': 'deleted'},
                             '111-33-b-5-v': {'op': 'deleted'}}, '111-22')
        builder = CFRChangeHTMLBuilder([], diffs)
        self.assertEqual(
            builder.diff_paths,
            {('111',), ('111', '22'), ('111', '22', 'a'), ('111', '33'),
             ('111', '33', 'b'), ('111', '33', 'b', '5'),
             ('111', '33', 'b', '5', 'v')})
