from unittest import TestCase

from mock import patch

from regulations.generator.api_reader import ApiReader


class ClientTest(TestCase):
    @patch('regulations.generator.api_reader._fetch')
    def test_regulation(self, fetch):
        to_return = {'example': 0, 'label': ['204'], 'children': []}
        fetch.return_value = to_return
        reader = ApiReader()
        self.assertEqual(to_return,
                         reader.regulation("label-here", "date-here"))
        self.assertTrue(fetch.called)
        param = fetch.call_args[0][0]
        self.assertTrue('label-here' in param)
        self.assertTrue('date-here' in param)

    @patch('regulations.generator.api_reader._fetch')
    def test_layer(self, fetch):
        to_return = {'example': 1}
        fetch.return_value = to_return
        reader = ApiReader()
        self.assertEqual(
            to_return,
            reader.layer("layer-here", "cfr", "label-here", "version-here"))
        self.assertEqual(1, fetch.call_count)
        param = fetch.call_args[0][0]
        self.assertIn('layer-here/cfr/version-here/label', param)
        self.assertNotIn('label-here', param)   # only grabs the root, "label"

        #   Cache
        self.assertEqual(
            to_return,
            reader.layer("layer-here", "cfr", "label-abc", "version-here"))
        self.assertEqual(1, fetch.call_count)

        self.assertEqual(
            to_return,
            reader.layer("layer-here", "cfr", "lablab", "version-here"))
        self.assertEqual(2, fetch.call_count)
        param = fetch.call_args[0][0]
        self.assertIn('layer-here/cfr/version-here/lablab', param)

        self.assertEqual(
            to_return,
            reader.layer("layer-here", "preamble", "lablab"))
        self.assertEqual(3, fetch.call_count)
        param = fetch.call_args[0][0]
        self.assertIn('layer-here/preamble/lablab', param)

    @patch('regulations.generator.api_reader._fetch')
    def test_notices(self, fetch):
        to_return = {'example': 1}
        fetch.return_value = to_return
        reader = ApiReader()
        self.assertEqual(to_return, reader.notices())
        self.assertTrue(fetch.called)

        self.assertEqual(to_return, reader.notices(part='p'))
        self.assertTrue(fetch.called)
        self.assertEqual({'part': 'p'}, fetch.call_args[0][1])

    @patch('regulations.generator.api_reader._fetch')
    def test_regversion(self, fetch):
        to_return = {}
        fetch.return_value = to_return
        reader = ApiReader()
        self.assertEqual(to_return, reader.regversions('765'))
        self.assertTrue(fetch.called)
        param = fetch.call_args[0][0]
        self.assertTrue('765' in param)

    @patch('regulations.generator.api_reader._fetch')
    def test_notice(self, fetch):
        to_return = {'example': 1}
        fetch.return_value = to_return
        reader = ApiReader()
        self.assertEqual(to_return, reader.notice("doc"))
        self.assertTrue(fetch.called)
        param = fetch.call_args[0][0]
        self.assertTrue('doc' in param)

    @patch('regulations.generator.api_reader._fetch')
    def test_diff(self, fetch):
        to_return = {'example': 1}
        fetch.return_value = to_return
        reader = ApiReader()
        self.assertEqual(to_return, reader.diff("204", "old", "new"))

        self.assertTrue(fetch.called)
        param = fetch.call_args[0][0]
        self.assertTrue('204' in param)
        self.assertTrue('old' in param)
        self.assertTrue('new' in param)

    @patch('regulations.generator.api_reader._fetch')
    def test_reg_cache(self, fetch):
        child = {
            'text': 'child',
            'node_type': 'interp',
            'children': [],
            'label': ['923', 'a', 'Interp'],
            'title': 'Some title'
        }
        child2 = {
            'text': 'child2',
            'node_type': 'interp',
            'children': [],
            'label': ['923', 'Interp', '1']
        }
        child3 = {
            'text': 'child',
            'node_type': 'interp',
            'children': [],
            'label': ['923', 'b', 'Interp'],
        }
        to_return = {
            'text': 'parent',
            'node_type': 'interp',
            'label': ['923', 'Interp'],
            'children': [child, child2, child3]
        }
        fetch.return_value = to_return
        reader = ApiReader()

        reader.regulation('923-Interp', 'ver')
        reader.regulation('923-Interp', 'ver')
        reader.regulation('923-a-Interp', 'ver')
        self.assertEqual(1, fetch.call_count)

        fetch.return_value = child2
        reader.regulation('923-Interp-1', 'ver')
        self.assertEqual(2, fetch.call_count)

        fetch.return_value = child3
        reader.regulation('923-b-Interp', 'ver')
        self.assertEqual(3, fetch.call_count)

        child = {
            'text': 'child',
            'children': [],
            'label': ['923', '1', 'a']
        }
        to_return = {
            'text': 'parent',
            'label': ['923', '1'],
            'children': [child]
        }
        fetch.reset_mock()
        fetch.return_value = to_return
        reader.regulation('923-1', 'ver')
        reader.regulation('923-1', 'ver')
        reader.regulation('923-1-a', 'ver')
        self.assertEqual(2, fetch.call_count)

    @patch('regulations.generator.api_reader._fetch')
    def test_cache_mutability(self, fetch):
        to_return = {
            'text': 'parent',
            'label': ['1024'],
            'children': []
        }
        fetch.return_value = to_return
        reader = ApiReader()

        result = reader.regulation('1024', 'ver')
        self.assertEqual(to_return, result)
        child = {
            'text': 'child',
            'children': [],
            'label': ['1024', 'a']
        }
        result['children'] = [child]

        second = reader.regulation('1024', 'ver')
        self.assertEqual(1, fetch.call_count)
        self.assertEqual(second, {'text': 'parent', 'label': ['1024'],
                                  'children': []})
