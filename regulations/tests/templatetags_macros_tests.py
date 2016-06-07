from unittest import TestCase
from xml.etree import ElementTree as etree  # nosec - see usage below

from django.template import Context, Template


class MacrosTests(TestCase):
    def _gen_link(self, content):
        """Shorthand for passing the content into a template and rendering"""
        text = "{% load macros %}" + content
        as_str = Template(text).render(Context({}))
        # Safe because: we've constructed the XML
        as_xml = etree.fromstring("<ROOT>{}</ROOT>".format(as_str))  # nosec
        anchors = as_xml.findall('.//a')
        self.assertTrue(len(anchors) > 0)
        return anchors[0]

    def test_external_link_no_optional(self):
        """The classes and title fields are optional. We should generate an
        appropriate link"""
        anchor = self._gen_link(
            '{% external_link url="http://example.com/path" text="Click" %}')
        self.assertEqual(anchor.get('target'), '_blank')
        self.assertEqual(anchor.get('href'), 'http://example.com/path')
        self.assertFalse('title' in anchor.attrib)
        self.assertTrue('aria-label' in anchor.attrib)
        self.assertTrue('Click' in anchor.text)

    def test_external_link_classes_title(self):
        """The classes and title fields _can_ be added"""
        anchor = self._gen_link(
            '{% external_link url="url" text="text" classes="some here" '
            'title="My Title" %}')
        self.assertEqual(anchor.get('title'), 'My Title')
        self.assertTrue('some here' in anchor.get('class'))

    def test_search_for(self):
        """Macro should url-encode search terms."""
        anchor = self._gen_link(
            '{% search_for terms="has spaces" reg="1234" version="vvv" %}')
        self.assertTrue('1234' in anchor.get('href'))
        self.assertTrue('vvv' in anchor.get('href'))
        self.assertTrue('has%20spaces' in anchor.get('href'))
