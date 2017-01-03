# vim: set encoding=utf-8
import unittest

from selenium.webdriver.support.ui import WebDriverWait

from regulations.uitests.base_test import BaseTest
from regulations.uitests import utils


class ScrollTest(BaseTest, unittest.TestCase):

    job_name = 'Scroll test'

    def test_scroll(self):
        self.driver.get(self.test_url + '/1005-36/2011-11111')

        header = self.driver.find_element_by_css_selector('.header-label')
        assert header.text == u'\xa7 1005.36'

        utils.scroll_to(self.driver, '#1005-36-a')
        WebDriverWait(self.driver, 5).until(
            lambda driver: header.text == u'\xa7 1005.36(a)')

        utils.scroll_to(self.driver, '#1005-36-a-2-iii')
        WebDriverWait(self.driver, 5).until(
            lambda driver: header.text == u'\xa7 1005.36(a)(2)(iii)')
