# vim: set fileencoding=utf-8
from unittest import TestCase
from regulations.generator.link_flattener import flatten_links


class LinkFlattenerTest(TestCase):
    def test_no_links(self):
        self.assertEqual("foo", flatten_links("foo"))

    def test_single_link(self):
        self.assertEqual(
            "<a href=foo> Fee Fie Foe </a>",
            flatten_links("<a href=foo> Fee Fie Foe </a>"))

    def test_unembedded_links(self):
        self.assertEqual(
            "<a href=foo> Fee </a> Fie <a href=bar> Foe </a>",
            flatten_links("<a href=foo> Fee </a> Fie <a href=bar> Foe </a>"))

    def test_embedded_link(self):
        self.assertEqual(
            "<a href=foo> Fee  Fie  Foe </a>",
            flatten_links("<a href=foo> Fee <a href=bar> Fie </a> Foe </a>"))
