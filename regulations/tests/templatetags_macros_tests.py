from unittest import TestCase

from django.template import Context, Template


class MacrosTests(TestCase):
    def _generate(self, content):
        """Shorthand for passing the content into a template and rendering"""
        text = "{% load macros %}" + content
        return Template(text).render(Context({}))

    def test_external_link_no_optional(self):
        """The classes and title fields are optional. We should generate an
        appropriate link"""
        result = self._generate(
            '{% external_link url="http://example.com/path" text="Click" %}')
        self.assertTrue('<a' in result)
        self.assertTrue('_blank' in result)
        self.assertFalse('title' in result)
        self.assertTrue('aria-label' in result)
        self.assertTrue('http://example.com/path' in result)
        self.assertTrue('Click' in result)

    def test_external_link_classes_title(self):
        """The classes and title fields _can_ be added"""
        result = self._generate(
            '{% external_link url="url" text="text" classes="some here" '
            'title="My Title" %}')
        self.assertTrue('title="My Title"' in result)
        self.assertTrue('some here' in result)

    def test_search_for(self):
        """Macro should url-encode search terms."""
        result = self._generate(
            '{% search_for terms="has spaces" reg="1234" version="vvv" %}')
        self.assertTrue('1234' in result)
        self.assertTrue('vvv' in result)
        self.assertTrue('has%20spaces' in result)
