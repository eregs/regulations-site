# vim: set encoding=utf-8
from unittest import TestCase

from mock import Mock

from regulations.generator.sidebar import analyses


class AnalysesSidebarTests(TestCase):
    def setUp(self):
        self.client = Mock()
        self.client.layer.return_value = {
            "111-22": [{"reference": ["2007-22", "111-22"],
                        "text": "Older analysis"},
                       {"reference": ["2009-11", "111-22"],
                        "text": "Newer analysis"}],
            "111-22-a": [{"reference": ["2009-22", "111-22-a"],
                          "text": "Paragraph analysis"}],
            '111-22-Interp': [{'reference': ['2007-22', '111-22-Interp']}],
            '111-22-Interp-2': [{'reference': ['2007-22', '111-22-Interp-2']}]
        }

    def test_context_section(self):
        self.client.regulation.return_value = {'label': ['111', '22']}
        self.assertEqual(
            analyses.Analyses('111-22', 'vvv').context(self.client, None),
            {'version': 'vvv',
             'human_label_id': u'§ 111.22',
             'analyses': [
                 {'doc_number': '2009-11', 'label_id': '111-22',
                  'text': u'§ 22'},
                 {'doc_number': '2009-22', 'label_id': '111-22-a',
                  'text': u'§ 22(a)'}
             ]})

    def test_context_paragraph(self):
        self.client.regulation.return_value = {"label": ['111', '22', 'a']}
        self.assertEqual(
            analyses.Analyses('111-22-a', 'vvv').context(self.client, None),
            {'version': 'vvv',
             'human_label_id': u'§ 111.22(a)',
             'analyses': [
                 {'doc_number': '2009-22', 'label_id': '111-22-a',
                  'text': u'§ 22(a)'}
             ]})

    def test_context_other_section(self):
        self.client.regulation.return_value = {"label": ['222', '22']}
        self.assertEqual(
            analyses.Analyses('222-22', 'vvv').context(self.client, None),
            {'version': 'vvv',
             'human_label_id': u'§ 222.22',
             'analyses': []})

    def test_context_interps(self):
        self.client.regulation.return_value = {
            "label": ['111', '22', 'Interp']}
        self.assertEqual(
            analyses.Analyses('111-22-Interp', 'vvv').context(self.client,
                                                              None),
            {'version': 'vvv',
             'human_label_id': 'Supplement to 111.22',
             'analyses': [
                 {'doc_number': '2007-22', 'label_id': '111-22-Interp',
                  'text': 'Supplement to 111.22'},
                 {'doc_number': '2007-22', 'label_id': '111-22-Interp-2',
                  'text': 'Supplement to 111.22-2'}
             ]})

    def test_context_interp_child(self):
        self.client.regulation.return_value = {
            "label": ['111', '22', 'Interp', '2']}
        self.assertEqual(
            analyses.Analyses('111-22-Interp-2', 'vvv').context(self.client,
                                                                None),
            {'version': 'vvv',
             'human_label_id': 'Supplement to 111.22-2',
             'analyses': [
                 {'doc_number': '2007-22', 'label_id': '111-22-Interp-2',
                  'text': 'Supplement to 111.22-2'}
             ]})
