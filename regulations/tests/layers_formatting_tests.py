from collections import defaultdict
from unittest import TestCase

from mock import Mock, patch

from regulations.generator.layers.formatting import FormattingLayer


class FormattingLayerTest(TestCase):
    def test_empty(self):
        """FormattingLayer ignores empty of missing node labels"""
        data = {'111-1': [], '111-2': [{}]}
        with patch('regulations.generator.layers.formatting.loader') as ldr:
            render = ldr.get_template.return_value.render
            fl = FormattingLayer(data)
        self.assertEqual([], fl.apply_layer('111-0'))
        self.assertEqual([], fl.apply_layer('111-1'))
        self.assertEqual([], fl.apply_layer('111-2'))
        self.assertFalse(render.called)

    def assert_context_contains(self, template_name, data_key, data_value,
                                expected_context=None):
        """Verify that FormattingLayer converts the `data` elements into a
        context variable similar to `expect_context`. If `expected_context` is
        not provided, assume that it should match `data_value`"""
        if expected_context is None:
            expected_context = dict(data_value)
        data = {'111-3': [{'text': 'original', 'locations': [0, 2],
                           data_key: data_value}]}
        template_file = 'regulations/layers/{}.html'.format(template_name)
        with patch('regulations.generator.layers.formatting.loader') as ldr:
            # we will want to reference these templates later
            templates = defaultdict(Mock)
            ldr.get_template.side_effect = templates.__getitem__
            fl = FormattingLayer(data)
            result = fl.apply_layer('111-3')
            render = templates[template_file].render

        self.assertEqual(len(result), 1)
        self.assertEqual('original', result[0][0])
        self.assertEqual([0, 2], result[0][2])

        self.assertTrue(render.called)
        context = render.call_args[0][0]
        for key, value in expected_context.iteritems():
            self.assertTrue(key in context)
            self.assertEqual(context[key], value)

    def test_apply_layer_table(self):
        data = {'header': [[{'colspan': 2, 'rowspan': 1, 'text': 'Title'}]],
                'rows': [['cell 11', 'cell 12'], ['cell 21', 'cell 22']]}
        self.assert_context_contains('table', 'table_data', data)

    def test_apply_layer_note(self):
        data = {'type': 'note',
                'lines': ['Note:', '1. Content1', '2. Content2']}
        expected = {'lines': ['1. Content1', '2. Content2'], 'type': 'note'}
        self.assert_context_contains('note', 'fence_data', data, expected)

    def test_apply_layer_code(self):
        data = {'type': 'python',
                'lines': ['def double(x):', '    return x + x']}
        self.assert_context_contains('code', 'fence_data', data)

    def test_apply_layer_subscript(self):
        data = {'variable': 'abc', 'subscript': '123'}
        self.assert_context_contains('subscript', 'subscript_data', data)

    def test_apply_layer_dash(self):
        data = {'text': 'This is an fp-dash'}
        self.assert_context_contains('dash', 'dash_data', data)

    def test_apply_layer_footnote(self):
        data = {'ref': '123', 'note': "Here's the note"}
        self.assert_context_contains('footnote', 'footnote_data', data)
