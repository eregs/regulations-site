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

    def test_get_layer_list(self):
        names = 'meta,meta,GRAPHICS,fakelayer,internal'
        layer_list = utils.get_layer_list(names)
        self.assertEquals(set(['meta', 'internal', 'graphics']), layer_list)

    @patch('regulations.generator.generator.LayerCreator.get_layer_json')
    def test_handle_specified_layers(self, get_layer_json):
        get_layer_json.return_value = {'layer': 'layer'}

        layer_names = 'graphics,meta'
        appliers = utils.handle_specified_layers(layer_names, '205', '2013-1')
        self.assertEquals(3, len(appliers))

    def test_add_extras_env(self):
        context = {}

        settings.JS_DEBUG = True
        utils.add_extras(context)
        self.assertEqual('source', context['env'])

        settings.JS_DEBUG = False
        utils.add_extras(context)
        self.assertEqual('built', context['env'])

        del(settings.JS_DEBUG)
        utils.add_extras(context)
        self.assertEqual('built', context['env'])

    def test_add_extras(self):
        context = {}
        settings.ANALYTICS = {
            'GOOGLE': {
                'GTM_SITE_ID': 'gtm-site-id',
                'GA_SITE_ID': 'ga-site-id',
                },
            'DAP': {
                'AGENCY': 'agency',
                'SUBAGENCY': 'sub-agency',
            }
        }

        utils.add_extras(context)

        self.assertTrue('APP_PREFIX' in context)
        self.assertTrue('env' in context)

        self.assertEquals('gtm-site-id',
                          context['ANALYTICS']['GOOGLE']['GTM_SITE_ID'])
        self.assertEquals('ga-site-id',
                          context['ANALYTICS']['GOOGLE']['GA_SITE_ID'])
        self.assertEquals('agency', context['ANALYTICS']['DAP']['AGENCY'])
        self.assertEquals('sub-agency',
                          context['ANALYTICS']['DAP']['SUBAGENCY'])
        self.assertEquals('agency=agency&subagency=sub-agency',
                          context['ANALYTICS']['DAP']['DAP_URL_PARAMS'])

    @patch('regulations.views.utils.fetch_toc')
    def test_first_section(self, fetch_toc):
        fetch_toc.return_value = [
            {'section_id': '204-100', 'index': ['204', '100']},
            {'section_id': '204-101', 'index': ['204', '101']}]
        first = utils.first_section('204', '2')
        self.assertEqual(first, '204-100')

    def test_make_sortable(self):
        """Verify that strings get decomposed correctly into sortable tuples"""
        self.assertEqual(utils.make_sortable("abc"), ("abc",))
        self.assertEqual(utils.make_sortable("123"), (123,))
        self.assertEqual(utils.make_sortable("abc123def456"),
                         ("abc", 123, "def", 456))
        self.assertEqual(utils.make_sortable("123abc456"), (123, "abc", 456))
