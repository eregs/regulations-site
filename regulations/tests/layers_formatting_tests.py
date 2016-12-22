from collections import defaultdict
from unittest import TestCase
from xml.etree import ElementTree as etree  # nosec - see usage below

from django.template import Context
from django.template.loader import get_template
from mock import Mock, patch

from regulations.generator.layers.formatting import FormattingLayer

template_loc = 'regulations/layers/{}.html'


class FormattingLayerTest(TestCase):
    def assert_context_contains(self, template_name, data_key, data_value,
                                expected_context=None):
        """Verify that FormattingLayer converts the `data` elements into a
        context variable similar to `expect_context`. If `expected_context` is
        not provided, assume that it should match `data_value`"""
        if expected_context is None:
            expected_context = dict(data_value)
        template_file = template_loc.format(template_name)
        with patch('regulations.generator.layers.formatting.loader') as ldr:
            # we will want to reference these templates later
            templates = defaultdict(Mock)
            ldr.get_template.side_effect = templates.__getitem__
            fl = FormattingLayer({})
            # materialize
            next(fl.replacements_for('', {data_key: data_value}))
            render = templates[template_file].render

        self.assertTrue(render.called)
        context = render.call_args[0][0]
        for key, value in expected_context.items():
            self.assertTrue(key in context)
            self.assertEqual(context[key], value)

    def render_html(self, template_name, data):
        template_file = template_loc.format(template_name)
        template = get_template(template_file)
        return template.render(Context(data))

    def test_replacements_for_table(self):
        data = {'header': [[{'colspan': 2, 'rowspan': 1, 'text': 'Title'}]],
                'rows': [['cell 11', 'cell 12'], ['cell 21', 'cell 22']]}
        self.assert_context_contains('table', 'table_data', data)
        output = self.render_html('table', data)
        # Safe because: output comes from our own markup
        tree = etree.fromstring(output)     # nosec
        self.assertEqual(1, len(tree.findall(".//table/thead")))
        self.assertEqual(0, len(tree.findall(".//table/caption")))
        self.assertEqual('Title', tree.findall(".//table/thead/tr/th")[0].text)

    def test_replacements_for_table_with_caption(self):
        data = {'header': [[{'colspan': 2, 'rowspan': 1, 'text': 'Title'}]],
                'rows': [['cell 11', 'cell 12'], ['cell 21', 'cell 22']],
                'caption': 'Caption'}
        self.assert_context_contains('table', 'table_data', data)
        output = self.render_html('table', data)
        # Safe because: output comes from our own markup
        tree = etree.fromstring(output)     # nosec
        self.assertEqual(1, len(tree.findall(".//table/caption")))
        self.assertEqual('Caption', tree.findall(".//table/caption")[0].text)

    def test_replacements_for_note(self):
        data = {'type': 'note',
                'lines': ['Note:', '1. Content1', '2. Content2']}
        expected = {'lines': ['1. Content1', '2. Content2'], 'type': 'note'}
        self.assert_context_contains('note', 'fence_data', data, expected)

    def test_replacements_for_code(self):
        data = {'type': 'python',
                'lines': ['def double(x):', '    return x + x']}
        self.assert_context_contains('code', 'fence_data', data)

    def test_replacements_for_subscript(self):
        data = {'subscript': '123'}
        self.assert_context_contains('subscript', 'subscript_data', data)

    def test_replacements_for_superscript(self):
        data = {'superscript': '123'}
        self.assert_context_contains('superscript', 'superscript_data', data)

    def test_replacements_for_dash(self):
        data = {'text': 'This is an fp-dash'}
        self.assert_context_contains('dash', 'dash_data', data)

    def test_replacements_for_footnote(self):
        data = {'ref': '123', 'note': "Here's the note"}
        self.assert_context_contains('footnote', 'footnote_data', data)
