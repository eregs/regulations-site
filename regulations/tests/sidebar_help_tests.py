from unittest import TestCase

from django.test import RequestFactory

from regulations.generator.sidebar import help


class HelpSidebarTests(TestCase):
    def setUp(self):
        self.req_factory = RequestFactory()
        self.sidebar = help.Help('111-11', 'vvvv')

    def test_context_default_subtemplates(self):
        """No request parameters should include multiple subtemplates"""
        result = self.sidebar.context(None, self.req_factory.get('/'))
        self.assertTrue(result['subtemplates'])

    def test_context_requested_subtemplates(self):
        """Specific request parameters should include only subtemplates which
        exist"""
        result = self.sidebar.context(
            None, self.req_factory.get('/?layers=internal,meta,fake,terms'))
        self.assertEqual(2, len(result['subtemplates']))
