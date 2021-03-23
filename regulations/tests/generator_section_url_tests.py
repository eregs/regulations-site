from unittest import TestCase

from regulations.generator.section_url import SectionUrl


class SectionUrlTest(TestCase):
    def test_of(self):
        url = SectionUrl.of(['303', '1'], 'ver-ver', False)
        self.assertEquals('#303-1', url)

        url = SectionUrl.of(['303', '1', 'b'], 'ver-ver', False)
        self.assertEquals('#303-1-b', url)

        url = SectionUrl.of(['303'], 'ver-ver', False)
        self.assertEquals('#303', url)

        url = SectionUrl.of(['303', '1', 'b'], 'ver-ver', True)
        self.assertEquals('/303/1/ver-ver/#303-1-b', url)

        self.assertTrue('999/88/ver-ver/#999-88-e' in
                        SectionUrl.of(['999', '88', 'e'], 'ver-ver', True))
        self.assertEqual(
            '#999-88-e', SectionUrl.of(['999', '88', 'e'], 'ver-ver', False))

        self.assertEqual(
            '#999-Subpart-Interp',
            SectionUrl.of(['999', 'Subpart', 'Interp'], 'ver-ver', False))
        self.assertEqual(
            '#999-Subpart-A-Interp',
            SectionUrl.of(['999', 'Subpart', 'A', 'Interp'], 'ver-ver', False))
        self.assertEqual(
            '#999-Appendices-Interp',
            SectionUrl.of(['999', 'Appendices', 'Interp'], 'ver-ver', False))
