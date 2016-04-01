from unittest import TestCase

from six.moves.urllib.parse import parse_qs
from django.template import RequestContext
from django.template.loader import get_template
from django.test import RequestFactory, SimpleTestCase, override_settings


class TemplateTest(TestCase):
    def test_title_in_base(self):
        context = {
            'env': 'dev',
            'reg_part': '204',
            'meta': {'cfr_title_number': '2'}}
        request = RequestFactory().get('/fake-path')
        c = RequestContext(request, context)
        t = get_template('regulations/base.html')
        rendered = t.render(c)

        title = '2 CFR Part 204 | eRegulations'
        self.assertTrue(title in rendered)


class GlobalContextTest(SimpleTestCase):

    @override_settings(JS_DEBUG=True)
    def test_debug(self):
        resp = self.client.get('/about')
        self.assertEqual(resp.context['EREGS_GLOBALS']['ENV'], 'source')

    @override_settings(JS_DEBUG=False)
    def test_prod(self):
        resp = self.client.get('/about')
        self.assertEqual(resp.context['EREGS_GLOBALS']['ENV'], 'built')

    @override_settings(
        ANALYTICS={
            'GOOGLE': {
                'GTM_SITE_ID': 'gtm-site-id',
                'GA_SITE_ID': 'ga-site-id',
            },
            'DAP': {
                'AGENCY': 'agency',
                'SUBAGENCY': 'sub-agency',
            },
        },
    )
    def test_analytics(self):
        resp = self.client.get('/about')
        analytics = resp.context['EREGS_GLOBALS']['ANALYTICS']
        self.assertEquals('gtm-site-id',
                          analytics['GOOGLE']['GTM_SITE_ID'])
        self.assertEquals('ga-site-id',
                          analytics['GOOGLE']['GA_SITE_ID'])
        self.assertEquals('agency', analytics['DAP']['AGENCY'])
        self.assertEquals('sub-agency',
                          analytics['DAP']['SUBAGENCY'])
        self.assertEquals(
            parse_qs('agency=agency&subagency=sub-agency'),
            parse_qs(analytics['DAP']['DAP_URL_PARAMS']),
        )

    def test_prefix(self):
        resp = self.client.get('/about')
        self.assertIn('APP_PREFIX', resp.context['EREGS_GLOBALS'])
