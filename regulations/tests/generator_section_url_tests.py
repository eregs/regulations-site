from unittest import TestCase

from mock import patch

from regulations.generator.section_url import SectionUrl


class SectionUrlTest(TestCase):
    @patch('regulations.generator.section_url.fetch_toc')
    def test_interp(self, fetch_toc):
        fetch_toc.return_value = [
            {'index': ['200', '1'], 'is_section': True},
            {'index': ['200', '2'], 'is_section': True},
            {'index': ['200', 'A'], 'is_appendix': True}]
        self.assertEqual('200-Subpart-Interp',
                         SectionUrl().interp(['200', '1', 'Interp'], 'ver-ver'))
        self.assertEqual('200-Subpart-Interp',
                         SectionUrl().interp(['200', '2', 'Interp'], 'ver-ver'))
        self.assertEqual('200-Appendices-Interp',
                         SectionUrl().interp(['200', 'A', 'Interp'], 'ver-ver'))

        fetch_toc.return_value = [
            {'index': ['200', 'Subpart', 'A'], 'is_subpart': True,
             'sub_toc': [{'index': ['200', '1'], 'is_section': True},
                         {'index': ['200', '2'], 'is_section': True}]},
            {'index': ['200', 'A'], 'is_appendix': True},
            {'index': ['200', 'Interp'], 'is_supplement': True,
             'sub_toc': [{'index': ['200', 'Interp', 'h1'],
                          'section_id': '200-Interp-h1'},
                         {'index': ['200', 'Subpart', 'A', 'Interp'],
                          'is_subterp': True},
                         {'index': ['200', 'Appendices', 'Interp'],
                          'is_subterp': True}]}]
        self.assertEqual('200-Subpart-A-Interp',
                         SectionUrl().interp(['200', '1', 'Interp'], 'ver-ver'))
        self.assertEqual('200-Subpart-A-Interp',
                         SectionUrl().interp(['200', '2', 'Interp'], 'ver-ver'))
        self.assertEqual('200-Appendices-Interp',
                         SectionUrl().interp(['200', 'A', 'Interp'], 'ver-ver'))
        self.assertEqual('200-Interp-h1',
                         SectionUrl().interp(['200', 'Interp', 'h1', 'p1'],
                                             'ver-ver'))
        self.assertEqual('200-Interp-h1',
                         SectionUrl().interp(['200', 'Interp', 'h1'], 'ver-ver'))
        self.assertTrue('200-Subpart-A',
                        SectionUrl().interp(['200', '2', 'e', 'Interp', '1'],
                                            'ver-ver'))

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
