from datetime import datetime, timedelta
import random
from unittest import TestCase

from mock import patch

from regulations.views.homepage import filter_future_amendments, get_regulations_list


class UniversalLandingTest(TestCase):
    """ Tests for the view that drives the main (universal) landing page. """

    def test_filter_future_amendments(self):
        versions = []
        futures = []

        today = datetime.today()
        for i in range(1, 5):
            future_date = today + timedelta(days=i)
            v = {'by_date': future_date}
            versions.append(v)
            futures.append(v)

        for i in range(1, 3):
            past_date = today - timedelta(days=i)
            versions.append({'by_date': past_date})

        random.shuffle(versions)

        self.assertEqual(len(versions), 6)
        filtered = filter_future_amendments(versions)
        self.assertEqual(len(filtered), 4)
        self.assertEqual(futures, filtered)

    def test_get_regulations_list_sort(self):
        """Verify that part numbers are sorted numerically rather than
        lexicographically"""
        version_info = [{'version': 'v', 'by_date': datetime(2001, 1, 1)}]
        versions = {'1': version_info, '2': version_info, '100': version_info}
        with patch('regulations.views.utils.regulation_meta'):
            with patch('regulations.views.utils.first_section'):
                results = get_regulations_list(versions)
                self.assertEqual(['1', '2', '100'],
                                 [r['part'] for r in results])
