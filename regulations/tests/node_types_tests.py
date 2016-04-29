# vim: set encoding=utf-8
from unittest import TestCase

from regulations.generator import node_types


class NodeTypesTest(TestCase):
    def test_change_appendix(self):
        node_parts_before = ['243', 'A', '30(a)']
        node_parts_after = node_types.to_markup_id(node_parts_before)
        node_string = "-".join(node_parts_after)

        self.assertEqual('243-A-30a', node_string)

    def test_type_from_label(self):
        for label in [('200', '5', 'A'), ('250',), ('250', '5'),
                      ('200', '5', 'a', 'i', 'C')]:
            self.assertEqual(node_types.REGTEXT,
                             node_types.type_from_label(label))

        for label in [('250', 'A2'), ('250', 'A'), ('250', 'A', '3(b)')]:
            self.assertEqual(node_types.APPENDIX,
                             node_types.type_from_label(label))

        for label in [('250', 'Interp'), ('250', 'A', 'Interp'),
                      ('250', 'A', 'Interp'), ('250', '5', 'b', 'Interp'),
                      ('250', '5', 'b', 'Interp', '1'),
                      ('250', '5', 'Interp', '5', 'r')]:
            self.assertEqual(node_types.INTERP,
                             node_types.type_from_label(label))

        self.assertEqual(node_types.EMPTYPART,
                         node_types.type_from_label(['250', 'Subpart']))
        self.assertEqual(node_types.SUBPART,
                         node_types.type_from_label(['250', 'Subpart', 'C']))

    def test_label_to_text(self):
        expectations = [
            (['2323', '4'], '2323.4'),
            (['2323', '5', 'r', '3'], '2323.5(r)(3)'),
            (['23', '5', 'r', '3', 'i', 'p12', 'A'], '23.5(r)(3)(i)'),
            (['23', '5', 'p1', 'a'], '23.5'),
            (['2323', 'A'], 'Appendix A to Part 2323'),
            (['2323', 'A', '4'], 'Appendix A-4'),
            (['2323', 'A', '4', 'b', '2'], 'Appendix A-4(b)(2)'),
            (['2323', '5', 'Interp'], 'Supplement to 2323.5'),
            (['2323', '7', 'b', 'Interp', '1', 'v'],
                'Supplement to 2323.7(b)-1.v'),
            (['2323', 'Z', 'Interp'], 'Supplement to Appendix Z to Part 2323'),
            (['204'], 'Regulation 204'),
            (['204', 'Interp'], 'Supplement I to Part 204'),
            (['204', 'Subpart', 'Interp'],
                'Interpretations for Regulation Text of Part 204'),
            (['204', 'Subpart', 'C', 'Interp'],
                'Interpretations for Subpart C of Part 204'),
            (['204', 'Appendices', 'Interp'],
                'Interpretations for Appendices of Part 204'),
            (['204', 'Interp', 'h1'], 'This Section'),
            (['204', 'M2'], 'Appendix M2 to Part 204')]
        for label, expected_text in expectations:
            self.assertEqual(expected_text, node_types.label_to_text(label))

        self.assertEqual('4', node_types.label_to_text(['2323', '4'], False))
        self.assertEqual(
            '5(r)(3)',
            node_types.label_to_text(['2323', '5', 'r', '3'], False))
        self.assertEqual(u'§ 2323.1',
                         node_types.label_to_text(['2323', '1'], True, True))
        self.assertEqual(u'§ 1',
                         node_types.label_to_text(['2323', '1'], False, True))
