from unittest import TestCase

from mock import patch

from regulations.generator.layers.paragraph_markers import (
    MarkerHidingLayer, MarkerInfoLayer, ParagraphMarkersLayer)


class ParagraphMarkersLayerTest(TestCase):
    @patch('regulations.generator.layers.paragraph_markers.loader')
    def test_replacements_for(self, loader):
        pml = ParagraphMarkersLayer({})
        result = list(pml.replacements_for('(a)', {}))
        self.assertEqual(1, len(result))
        call_args = loader.get_template.return_value.render.call_args[0][0]
        self.assertEqual('(a)', call_args['paragraph'])
        self.assertEqual('a', call_args['paragraph_stripped'])

        result = list(pml.replacements_for('q.', {}))
        self.assertEqual(1, len(result))
        call_args = loader.get_template.return_value.render.call_args[0][0]
        self.assertEqual('q.', call_args['paragraph'])
        self.assertEqual('q', call_args['paragraph_stripped'])


class MarkerHidingLayerTest(TestCase):
    @patch('regulations.generator.layers.paragraph_markers.loader')
    def test_replacements_for(self, loader):
        mhl = MarkerHidingLayer({})
        result = list(mhl.replacements_for('(a)', {}))
        self.assertEqual(1, len(result))
        call_args = loader.get_template.return_value.render.call_args[0][0]
        self.assertEqual('(a)', call_args['paragraph'])

        result = list(mhl.replacements_for('q.', {}))
        self.assertEqual(1, len(result))
        call_args = loader.get_template.return_value.render.call_args[0][0]
        self.assertEqual('q.', call_args['paragraph'])


class MarkerInfoLayerTest(TestCase):
    def test_attach_metadata(self):
        mil = MarkerInfoLayer({
            '1001-12-a': [{'text': '(a)', 'locations': [0]}],
            '1001-12-q': [{'text': 'q.', 'locations': [1]}]
        })
        node = {'label_id': '1002-01-01'}
        mil.attach_metadata(node)
        self.assertEqual(set(node.keys()), {'label_id'})

        node['label_id'] = '1001-12-a'
        mil.attach_metadata(node)
        self.assertEqual(node['paragraph_marker'], 'a')

        node['label_id'] = '1001-12-q'
        mil.attach_metadata(node)
        self.assertEqual(node['paragraph_marker'], 'q')
