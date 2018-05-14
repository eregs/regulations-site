from unittest import TestCase

from regulations.generator.layers.footnotes import FootnotesLayer


class FootnotesLayerTest(TestCase):
    def test_single_note(self):
        layer = {
            "555-220-p1": [
                {
                    "footnote_data": {
                        "note": "Some notes",
                        "ref": "1"
                    },
                    "locations": [
                        0
                    ],
                    "text": "[^1]Some actual text"
                }
            ]
        }
        node = {'label_id': '555-220'}
        FootnotesLayer(layer).attach_metadata(node)
        self.assertEqual(node['footnotes'],
                         [{'ref': '1', 'note': 'Some notes'}])

    def test_sorted_multiple_notes(self):
        layer = {
            "555-220-p1": [
                {
                    "footnote_data": {
                        "note": "Third notes",
                        "ref": "3"
                    },
                    "locations": [
                        0
                    ],
                    "text": "[^3]Some actual text"
                },
                {
                    "footnote_data": {
                        "note": "First notes",
                        "ref": "1"
                    },
                    "locations": [
                        0
                    ],
                    "text": "[^1]Some actual text"
                },
                {
                    "footnote_data": {
                        "note": "Second notes",
                        "ref": "2"
                    },
                    "locations": [
                        0
                    ],
                    "text": "[^2]Some actual text"
                }
            ]
        }
        node = {'label_id': '555-220'}
        FootnotesLayer(layer).attach_metadata(node)
        self.assertEqual(node['footnotes'],
                         [{'ref': '1', 'note': 'First notes'},
                          {'ref': '2', 'note': 'Second notes'},
                          {'ref': '3', 'note': 'Third notes'}])

    def test_multiple_children(self):
        layer = {
            "555-220-p1": [
                {
                    "footnote_data": {
                        "note": "First notes",
                        "ref": "1"
                    },
                    "locations": [
                        0
                    ],
                    "text": "[^1]Some actual text"
                }
            ],
            "555-220-p2": [
                {
                    "footnote_data": {
                        "note": "Second notes",
                        "ref": "2"
                    },
                    "locations": [
                        0
                    ],
                    "text": "[^1]Some actual text"
                }
            ]
        }
        node = {'label_id': '555-220'}
        FootnotesLayer(layer).attach_metadata(node)
        self.assertEqual(node['footnotes'],
                         [{'ref': '1', 'note': 'First notes'},
                          {'ref': '2', 'note': 'Second notes'}])
