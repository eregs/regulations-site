# vim: set encoding=utf-8
import unittest

from nose.tools import *  # noqa
from selenium.webdriver.support.ui import WebDriverWait

from regulations.uitests.base_test import BaseTest


def scroll_to(driver, selector):
    cmd = 'window.scroll(0, $("{selector}").offset().top)'.format(
        selector=selector)
    driver.execute_script(cmd)


class ScrollTest(BaseTest, unittest.TestCase):

    job_name = 'Scroll test'

    def test_scroll(self):
        self.driver.get(self.test_url + '/1005-36/2011-11111')

        header = self.driver.find_element_by_css_selector('.header-label')
        assert_equal(header.text, u'\xa71005.36')

        scroll_to(self.driver, '#1005-36-a')
        WebDriverWait(self.driver, 5).until(
            lambda driver: header.text == u'\xa71005.36(a)')

        scroll_to(self.driver, '#1005-36-a-2-iii')
        WebDriverWait(self.driver, 5).until(
            lambda driver: header.text == u'\xa71005.36(a)(2)(iii)')
