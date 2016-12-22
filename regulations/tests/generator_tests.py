from unittest import TestCase

from mock import patch

from regulations.generator import generator


class GeneratorTest(TestCase):
    @patch('regulations.generator.generator.api_reader')
    def test_get_tree_paragraph(self, api_reader):
        node = {'some': 'text'}
        api_reader.ApiReader.return_value.regulation.return_value = node

        p = generator.get_tree_paragraph('some-id', 'some-version')
        self.assertEqual(node, p)
        self.assertEqual(
            ('some-id', 'some-version'),
            api_reader.ApiReader.return_value.regulation.call_args[0])

    @patch('regulations.generator.generator.api_reader')
    def test_get_diff_json(self, api_reader):
        diff = {'some': 'diff'}
        api_reader.ApiReader.return_value.diff.return_value = diff
        d = generator.get_diff_json('204', 'old', 'new')
        self.assertEqual(diff, d)
        self.assertEqual(
            ('204', 'old', 'new'),
            api_reader.ApiReader.return_value.diff.call_args[0])

    @patch('regulations.generator.generator.api_reader')
    def test_get_notice(self, api_reader):
        notice = {'some': 'notice'}
        api_reader.ApiReader.return_value.notice.return_value = notice
        n = generator.get_notice('204-1234')
        self.assertEqual(notice, n)
        self.assertEqual(
            ('204-1234',),
            api_reader.ApiReader.return_value.notice.call_args[0])

    @patch('regulations.generator.generator.get_diff_json')
    def test_get_diff_applier(self, get_diff_json):
        diff = {'some': 'diff'}
        get_diff_json.return_value = diff
        da = generator.get_diff_applier('204', 'old', 'new')
        self.assertEqual(da.diff, diff)
        self.assertEqual(
            ('204', 'old', 'new'),
            get_diff_json.call_args[0])

    @patch('regulations.generator.generator.get_diff_json')
    def test_get_diff_applier_allows_empty(self, get_diff_json):
        diff = {}
        get_diff_json.return_value = diff
        da = generator.get_diff_applier('204', 'old', 'new')
        self.assertEqual(da.diff, diff)
        self.assertEqual(
            ('204', 'old', 'new'),
            get_diff_json.call_args[0])
