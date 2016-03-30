from unittest import TestCase

from regulations.generator.label import Label


class LabelTests(TestCase):
    def test_sort_roman(self):
        """ Here we ensure that roman numerals are sorted correctly. """
        labels = [Label('200-20-d-2-viii'),
                  Label('200-20-d-2-ix'),
                  Label('200-20-d-2-iv'),
                  Label('200-20-d-2-v'),
                  Label('200-20-d-2-vi'),
                  Label('200-20-d-2-x'),
                  Label('200-20-d-2-xi')]
        labels = list(sorted(labels))
        self.assertEqual(labels, [Label('200-20-d-2-iv'),
                                  Label('200-20-d-2-v'),
                                  Label('200-20-d-2-vi'),
                                  Label('200-20-d-2-viii'),
                                  Label('200-20-d-2-ix'),
                                  Label('200-20-d-2-x'),
                                  Label('200-20-d-2-xi')])
