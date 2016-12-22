# vim: set fileencoding=utf-8
from unittest import TestCase

from regulations.generator.layers.toc_applier import (
    TableOfContentsLayer)


class TableOfContentsLayerTest(TestCase):
    def test_section(self):
        toc = TableOfContentsLayer(None)
        el = {}
        toc.section(el, {'index': ['1']})
        self.assertEqual({}, el)

        toc.section(el, {'index': ['1', '2', '3']})
        self.assertEqual({}, el)

        toc.section(el, {'index': ['1', 'B']})
        self.assertEqual({}, el)

        toc.section(el, {'index': ['1', 'Interpretations']})
        self.assertEqual({}, el)

        toc.section(el, {'index': ['1', '2'], 'title': u'§ 1.2 - Awesome'})
        self.assertEqual(el, {
            'is_section': True,
            'is_section_span': False,
            'section_id': '1-2',
            'label': '1.2',
            'sub_label': 'Awesome'
        })

        toc.section(el, {'index': ['2', '1'], 'title': u'§ 2.1 Sauce'})
        self.assertEqual(el, {
            'is_section': True,
            'is_section_span': False,
            'section_id': '2-1',
            'label': '2.1',
            'sub_label': 'Sauce'
        })

    def test_section_with_thin_space(self):
        toc = TableOfContentsLayer(None)
        el = {}
        toc.section(el, {'index': ['1', '2'], 'title': u'§ 1.2 -  Awesome'})
        self.assertEqual(el, {
            'is_section': True,
            'is_section_span': False,
            'section_id': '1-2',
            'label': '1.2',
            'sub_label': 'Awesome'
        })

    def test_section_span(self):
        toc = TableOfContentsLayer(None)
        el = {}

        toc.section(el, {
            'index': ['1', '2'],
            'title': u'§§ 1.2-6 - This is a span'
        })
        self.assertEqual(el, {
            'is_section': True,
            'is_section_span': True,
            'section_id': '1-2',
            'label': '1.2-6',
            'sub_label': 'This is a span'
        })

    def test_appendix_supplement(self):
        toc = TableOfContentsLayer(None)
        el = {}
        toc.appendix_supplement(el, {'index': ['1']})
        self.assertEqual({}, el)

        toc.appendix_supplement(el, {'index': ['1', '2', '3']})
        self.assertEqual({}, el)

        toc.appendix_supplement(el, {'index': ['1', 'B', '3']})
        self.assertEqual({}, el)

        toc.appendix_supplement(el, {'index': ['1', 'Interp', '3']})
        self.assertEqual({}, el)

        toc.appendix_supplement(el, {
            'index': ['1', 'B'],
            'title': 'Appendix B - Bologna'})
        self.assertEqual(el, {
            'is_appendix': True,
            'is_first_appendix': True,
            'label': 'Appendix B',
            'sub_label': 'Bologna',
            'section_id': '1-B'
        })

        el = {}
        toc.appendix_supplement(el, {
            'index': ['204', 'A'],
            'title': 'Appendix A to Part 204 - Model Forms'})
        self.assertEqual(el, {
            'is_appendix': True,
            'is_first_appendix': True,
            'label': 'Appendix A to Part 204',
            'sub_label': 'Model Forms',
            'section_id': '204-A'
        })

        el = {}
        toc.appendix_supplement(el, {
            'index': ['1', 'Interp'],
            'title': 'Supplement I to 8787 - I am Iron Man'})
        self.assertEqual(el, {
            'is_supplement': True,
            'label': 'Supplement I to 8787',
            'sub_label': 'I am Iron Man',
            'section_id': '1-Interp'
        })

    def test_attach_metadata_url(self):
        toc = TableOfContentsLayer({'100': [
            {'title': u'§ 100.1 Intro', 'index': ['100', '1']}]})

        node = {'label_id': '100'}
        toc.attach_metadata(node)
        self.assertEqual('#100-1', node['TOC'][0]['url'])

        toc.sectional = True
        toc.version = 'verver'
        toc.attach_metadata(node)
        self.assertTrue('100-1/verver#100-1' in node['TOC'][0]['url'])

    def test_attach_metadata_compatibility(self):
        toc = TableOfContentsLayer({'100': [
            {'title': u'§ 100.1 Intro', 'index': ['100', '1']},
            {'title': 'Appendix A', 'index': ['100', 'A']},
            {'title': 'Supplement I', 'index': ['100', 'Interp']}]})
        node = {'label_id': '100'}
        toc.attach_metadata(node)
        self.assertEqual(3, len(node['TOC']))

        toc = TableOfContentsLayer({
            '100': [
                {'title': 'Subpart A', 'index': ['100', 'Subpart', 'A']},
                {'title': 'Appendix A', 'index': ['100', 'A']},
                {'title': 'Supplement I', 'index': ['100', 'Interp']}],
            '100-Subpart-A': [
                {'title': u'§ 100.1 Intro', 'index': ['100', '1']},
                {'title': u'§ 100.2 Sec2', 'index': ['100', '2']},
                {'title': u'§ 100.3 Sec3', 'index': ['100', '3']}]
            })
        toc.attach_metadata(node)
        self.assertEqual(3, len(node['TOC']))
        self.assertEqual(3, len(node['TOC'][0]['sub_toc']))

    def test_attach_metadata_first_appendix(self):
        toc = TableOfContentsLayer({'100': [
            {'title': 'Appendix A', 'index': ['100', 'A']},
            {'title': 'Appendix B', 'index': ['100', 'B']},
            {'title': 'Appendix C', 'index': ['100', 'C']},
            {'title': 'Supplement I', 'index': ['100', 'Interp']}]})
        node = {'label_id': '100'}
        toc.attach_metadata(node)
        self.assertEqual(4, len(node['TOC']))
        aA, aB, aC, sI = node['TOC']
        self.assertTrue(aA['is_first_appendix'])
        self.assertFalse(aB['is_first_appendix'])
        self.assertFalse(aC['is_first_appendix'])
        self.assertFalse(sI.get('is_first_appendix', False))

        toc = TableOfContentsLayer({'100': [
            {'title': 'Supplement I', 'index': ['100', 'Interp']}]})
        toc.attach_metadata(node)
        self.assertEqual(1, len(node['TOC']))
        self.assertFalse(node['TOC'][0].get('is_first_appendix', False))

    def test_attach_metadata_interp_emptysubpart(self):
        toc = TableOfContentsLayer({'100': [
            {'title': u'§ 100.1 Intro', 'index': ['100', '1']},
            {'title': u'§ 100.2 Second', 'index': ['100', '2']},
            {'title': 'Supplement I', 'index': ['100', 'Interp']}]})
        node = {'label_id': '100'}
        toc.attach_metadata(node)
        self.assertEqual(3, len(node['TOC']))
        s1, s2, interp = node['TOC']
        self.assertEqual(1, len(interp['sub_toc']))
        nosubpart = interp['sub_toc'][0]
        self.assertEqual('Regulation Text', nosubpart['label'])
        self.assertEqual(['100', 'Subpart', 'Interp'], nosubpart['index'])

        toc = TableOfContentsLayer({'100': [
            {'title': u'§ 100.1 Intro', 'index': ['100', '1']},
            {'title': u'§ 100.2 Second', 'index': ['100', '2']},
            {'title': 'Appendix A', 'index': ['100', 'A']},
            {'title': 'Appendix C', 'index': ['100', 'C']},
            {'title': 'Supplement I', 'index': ['100', 'Interp']}]})
        toc.attach_metadata(node)
        self.assertEqual(5, len(node['TOC']))
        s1, s2, appA, appC, interp = node['TOC']
        self.assertEqual(2, len(interp['sub_toc']))
        nosubpart, appendices = interp['sub_toc']
        self.assertEqual('Regulation Text', nosubpart['label'])
        self.assertEqual(['100', 'Subpart', 'Interp'], nosubpart['index'])
        self.assertEqual('Appendices', appendices['label'])
        self.assertEqual(['100', 'Appendices', 'Interp'], appendices['index'])

    def test_attach_metadata_interp_subparts(self):
        toc = TableOfContentsLayer({
            '100': [
                {'title': 'Subpart A', 'index': ['100', 'Subpart', 'A']},
                {'title': 'Supplement I', 'index': ['100', 'Interp']}],
            '100-Subpart-A': [
                {'title': u'§ 100.1 Intro', 'index': ['100', '1']},
                {'title': u'§ 100.2 Second', 'index': ['100', '2']}]})
        node = {'label_id': '100'}
        toc.attach_metadata(node)
        self.assertEqual(2, len(node['TOC']))
        subpartA, interp = node['TOC']
        self.assertEqual(2, len(subpartA['sub_toc']))
        self.assertEqual(1, len(interp['sub_toc']))
        nosubpart = interp['sub_toc'][0]
        self.assertEqual('Subpart A', nosubpart['label'])
        self.assertEqual(['100', 'Subpart', 'A', 'Interp'], nosubpart['index'])

        toc = TableOfContentsLayer({
            '100': [
                {'title': 'Subpart A', 'index': ['100', 'Subpart', 'A']},
                {'title': 'Appendix A', 'index': ['100', 'A']},
                {'title': 'Appendix C', 'index': ['100', 'C']},
                {'title': 'Supplement I', 'index': ['100', 'Interp']}],
            '100-Subpart-A': [
                {'title': u'§ 100.1 Intro', 'index': ['100', '1']},
                {'title': u'§ 100.2 Second', 'index': ['100', '2']}]})
        node = {'label_id': '100'}
        toc.attach_metadata(node)
        self.assertEqual(4, len(node['TOC']))
        subpartA, appA, appC, interp = node['TOC']
        self.assertEqual(2, len(interp['sub_toc']))
        nosubpart, appendices = interp['sub_toc']
        self.assertEqual('Subpart A', nosubpart['label'])
        self.assertEqual(['100', 'Subpart', 'A', 'Interp'], nosubpart['index'])
        self.assertEqual('Appendices', appendices['label'])
        self.assertEqual(['100', 'Appendices', 'Interp'], appendices['index'])
