# vim: set encoding=utf-8
from unittest import TestCase
from mock import patch

from django.conf import settings

from regulations.views import utils


class UtilsTest(TestCase):
    def setUp(self):

        if hasattr(settings, 'ANALYTICS'):
            self.old_analytics = settings.ANALYTICS
        if hasattr(settings, 'JS_DEBUG'):
            self.old_js_debug = settings.JS_DEBUG

    def tearDown(self):
        if hasattr(self, 'old_analytics'):
            settings.ANALYTICS = self.old_analytics

        if hasattr(self, 'old_js_debug'):
            settings.JS_DEBUG = self.old_js_debug

    @patch('regulations.views.utils.fetch_toc')
    def test_first_section(self, fetch_toc):
        fetch_toc.return_value = [
            {'section_id': '204-100', 'index': ['204', '100']},
            {'section_id': '204-101', 'index': ['204', '101']}]
        first = utils.first_section('204', '2')
        self.assertEqual(first, '100')

    def test_make_sortable(self):
        """Verify that strings get decomposed correctly into sortable tuples"""
        self.assertEqual(utils.make_sortable("abc"), ("abc",))
        self.assertEqual(utils.make_sortable("123"), (123,))
        self.assertEqual(utils.make_sortable("abc123def456"),
                         ("abc", 123, "def", 456))
        self.assertEqual(utils.make_sortable("123abc456"), (123, "abc", 456))

    @patch('regulations.views.utils.api_reader')
    def test_regulation_meta_404(self, api_reader):
        """We shouldn't crash if meta data isn't available"""
        ret_vals = [None, {}, {'111-22': 'something'}]
        for ret_val in ret_vals:
            api_reader.ApiReader.return_value.layer.return_value = ret_val
            self.assertEqual({}, utils.regulation_meta('111', 'ver-ver'))
