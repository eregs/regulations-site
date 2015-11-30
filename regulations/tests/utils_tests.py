from unittest import TestCase

from regulations import utils


class UtilsTests(TestCase):
    def test_make_sortable(self):
        """Verify that strings get decomposed correctly into sortable tuples"""
        self.assertEqual(utils.make_sortable("abc"), ("abc",))
        self.assertEqual(utils.make_sortable("123"), (123,))
        self.assertEqual(utils.make_sortable("abc123def456"),
                         ("abc", 123, "def", 456))
        self.assertEqual(utils.make_sortable("123abc456"), (123, "abc", 456))
