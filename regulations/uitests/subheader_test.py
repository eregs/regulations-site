import unittest

from regulations.uitests.base_test import BaseTest


class SubheaderTests(BaseTest, unittest.TestCase):
    def job_name(self):
        return 'Subheader tests'

    def test_effective_date(self):
        self.driver.get(self.test_url + '/1005-1/2012-12121')
        effective = self.driver.find_element_by_class_name('effective-date')
        self.assertIn('10/28/2012', effective.text)
