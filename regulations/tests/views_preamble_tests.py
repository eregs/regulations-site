from unittest import TestCase

from django.test import RequestFactory
from mock import patch

from regulations.views import preamble


class PreambleViewTests(TestCase):
    _mock_preamble = {
        'text': '1', 'label': ['1'], 'children': [
            {'text': '2', 'label': ['1', 'c'], 'children': [
                {'text': '3', 'label': ['1', 'c', 'i'], 'children': []},
                {'text': '4', 'label': ['1', 'c', 'x'], 'children': []}
            ]},
            {'text': '5', 'label': ['1', '1'], 'children': []}
        ]
    }

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

    @patch('regulations.views.preamble.ApiReader')
    def test_get_integration(self, ApiReader):
        """Verify that the contexts are built correctly before being sent to
        the template. AJAX/partial=true requests should only get the inner
        context (i.e. no UI-related context)"""
        ApiReader.return_value.preamble.return_value = self._mock_preamble
        view = preamble.PreambleView.as_view()

        response = view(RequestFactory().get('/preamble/1/c/x'),
                        paragraphs='1/c/x')
        self.assertEqual(
            response.context_data['sub_context']['node']['text'], '4')
        self.assertEqual(
            response.context_data['sub_context']['node']['children'], [])
        self.assertEqual(response.context_data['preamble'],
                         self._mock_preamble)
        self.assertNotIn('node', response.context_data)

        response = view(RequestFactory().get('/preamble/1/c/x?partial=true'),
                        paragraphs='1/c/x')
        self.assertNotIn('sub_context', response.context_data)
        self.assertEqual(response.context_data['node']['text'], '4')

        request = RequestFactory().get(
            '/preamble/1/c/x',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = view(request, paragraphs='1/c/x')
        self.assertNotIn('sub_context', response.context_data)
        self.assertEqual(response.context_data['node']['text'], '4')
