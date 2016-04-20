from unittest import TestCase

from regulations.generator import notices


class NoticesTest(TestCase):
    def test_find_label_in_sxs_found(self):
        sxs_list = [
            {'label': '204-1', 'children': []},
            {'label': '204-2', 'children': [{
                'label': '204-2-a',
                'children': [
                    {'label': '204-3', 'children': [], 'paragraphs': ['x']}],
                'paragraphs': ['abc']}]}]

        s = notices.find_label_in_sxs(sxs_list, '204-2-a')
        self.assertEqual('204-2-a', s['label'])
        self.assertEqual(['abc'], s['paragraphs'])

        s = notices.find_label_in_sxs(sxs_list, '204-3')
        self.assertEqual('204-3', s['label'])
        self.assertEqual(['x'], s['paragraphs'])

        sxs_list = [
            {'labels': ['204-1'], 'children': []},
            {'labels': ['204-2'], 'children': [{
                'labels': ['204-2-a', '204-2-b'],
                'children': [
                    {'labels': ['204-3'], 'children': [],
                     'paragraphs': ['x']}],
                'paragraphs': ['abc']}]}]

        s = notices.find_label_in_sxs(sxs_list, '204-2-b')
        self.assertEqual(['204-2-a', '204-2-b'], s['labels'])
        self.assertEqual(['abc'], s['paragraphs'])

        s = notices.find_label_in_sxs(sxs_list, '204-3')
        self.assertEqual(['204-3'], s['labels'])
        self.assertEqual(['x'], s['paragraphs'])

    def test_find_label_in_sxs_top_no_label(self):
        sxs_list = [
            {'title': 'Awesome, SXS title here', 'children': [
                {'label': '204-3', 'children': [], 'paragraphs': ['x']}],
                'paragraphs': ['abc']}]

        s = notices.find_label_in_sxs(sxs_list, '204-3')
        self.assertEqual('204-3', s['label'])
        self.assertEqual(['x'], s['paragraphs'])

        sxs_list = [
            {'title': 'Awesome, SXS title here', 'children': [
                {'labels': ['204-3'], 'children': [], 'paragraphs': ['x']}],
                'paragraphs': ['abc']}]

        s = notices.find_label_in_sxs(sxs_list, '204-3')
        self.assertEqual(['204-3'], s['labels'])
        self.assertEqual(['x'], s['paragraphs'])

    def test_find_label_in_sxs_page(self):
        sxs_list = [
            {'labels': ['204-3'], 'page': 1234, 'paragraphs': ['a'],
             'children': [
                {'labels': ['204-3-a'], 'page': 1234, 'paragraphs': ['b'],
                 'children': []}]},
            {'labels': ['204-3'], 'page': 3456, 'paragraphs': ['c'],
             'children': [
                {'labels': ['204-3-a'], 'page': 3457, 'paragraphs': ['d'],
                 'children': []},
                {'labels': ['204-3-a'], 'page': 3460, 'paragraphs': ['e'],
                 'children': []}]}]

        s = notices.find_label_in_sxs(sxs_list, '204-3')
        self.assertEqual(['a'], s['paragraphs'])
        s = notices.find_label_in_sxs(sxs_list, '204-3', 1234)
        self.assertEqual(['a'], s['paragraphs'])
        s = notices.find_label_in_sxs(sxs_list, '204-3', 9999)
        self.assertEqual(['a'], s['paragraphs'])
        s = notices.find_label_in_sxs(sxs_list, '204-3', 3456)
        self.assertEqual(['c'], s['paragraphs'])

        s = notices.find_label_in_sxs(sxs_list, '204-3-a')
        self.assertEqual(['b'], s['paragraphs'])
        s = notices.find_label_in_sxs(sxs_list, '204-3-a', 1234)
        self.assertEqual(['b'], s['paragraphs'])
        s = notices.find_label_in_sxs(sxs_list, '204-3-a', 9999)
        self.assertEqual(['b'], s['paragraphs'])
        s = notices.find_label_in_sxs(sxs_list, '204-3-a', 3457)
        self.assertEqual(['d'], s['paragraphs'])
        s = notices.find_label_in_sxs(sxs_list, '204-3-a', 3460)
        self.assertEqual(['e'], s['paragraphs'])

    def test_non_empty_sxs(self):
        sxs = {'label': '204-2-a', 'children': [], 'paragraphs': ['abc']}
        self.assertTrue(notices.non_empty_sxs(sxs))

    def test_non_empty_sxs_no_paragraph(self):
        sxs = {'label': '204-2-a', 'children': [], 'paragraphs': []}
        self.assertFalse(notices.non_empty_sxs(sxs))

    def test_non_empty_sxs_has_children(self):
        sxs = {
            'label': '204-2-a',
            'children': [{'title': 'abc'}],
            'paragraphs': []}
        self.assertTrue(notices.non_empty_sxs(sxs))

    def test_find_label_in_sxs_not_found(self):
        sxs_list = [
            {'label': '204-1', 'children': []},
            {'label': '204-2', 'children': [{
                'label': '204-2-a',
                'children': []}]}]

        s = notices.find_label_in_sxs(sxs_list, '202-a')
        self.assertEqual(None, s)

    def test_filter_children(self):
        sxs = {'children': [
            {'label': '204-a', 'paragraphs': ['me']},
            {'paragraphs': ['abcd']}]}
        filtered = notices.filter_labeled_children(sxs)
        self.assertEqual(filtered, [{'paragraphs': ['abcd']}])

    def test_filter_children_no_candidates(self):
        sxs = {'children': [
            {'label': '204-a', 'paragraphs': ['me']},
            {'label': '204-b', 'paragraphs': ['abcd']}]}
        filtered = notices.filter_labeled_children(sxs)
        self.assertEqual(filtered, [])

    def test_add_depths(self):
        sxs = {
            'label': '204-2',
            'children': [{
                'label': '204-2-a',
                'children': [],
                'paragraphs': ['abc']}]}
        notices.add_depths(sxs, 3)
        depth_sxs = {
            'label': '204-2',
            'depth': 3,
            'children': [{
                'depth': 4,
                'label': '204-2-a',
                'children': [],
                'paragraphs': ['abc']}]}
        self.assertEqual(depth_sxs, sxs)
