from unittest import TestCase
from django.urls import reverse


class UrlTests(TestCase):
    def test_chrome_section_url(self):
        r = reverse('reader_view', args=('201', '2', '2012-1123'))
        self.assertEqual(r, '/201/2/2012-1123/')

        r = reverse(
            'reader_view', args=('201', '2', '2012-1123_20121011'))
        self.assertEqual(r, '/201/2/2012-1123_20121011/')
