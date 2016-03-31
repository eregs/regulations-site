from unittest import TestCase

from django.http import Http404
from django.test import RequestFactory
from mock import patch

from regulations.views import preamble


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

    @patch('regulations.generator.generator.api_reader')
    @patch('regulations.views.preamble.ApiReader')
    def test_get_integration(self, ApiReader, api_reader):
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
        self.assertIn('env', response.context_data)
        self.assertEqual(
            response.context_data['sub_context']['node']['text'], '4')
        self.assertEqual(
            response.context_data['sub_context']['node']['children'], [])
        # layer data is present
        self.assertEqual(
            response.context_data['sub_context']['node']['meta'], 'something')
        self.assertEqual(response.context_data['preamble'],
                         self._mock_preamble)
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
