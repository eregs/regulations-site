import unittest

from nose.tools import *  # noqa
from selenium.webdriver.support.ui import WebDriverWait

from regulations.uitests.base_test import BaseTest


class CommentTest(BaseTest, unittest.TestCase):

    job_name = 'Comment test'

    def test_comment(self):
        self.driver.get(self.test_url + '/preamble/2016_02749/I')
        html = self.driver.find_element_by_tag_name('html')
        WebDriverWait(self.driver, 60).until(
            lambda driver: 'selenium-start' in html.get_attribute('class'))

        # Open write mode for a section
        comment_toggle = self.driver.find_element_by_css_selector(
            '.activate-write')
        comment_label = comment_toggle.get_attribute('data-label')
        comment_toggle.click()

        # Comment index starts empty
        index_items = self.driver.find_elements_by_css_selector(
            '.comment-index-item')
        assert_equal(len(index_items), 0)

        # Write and save a comment
        textarea = self.driver.find_element_by_css_selector(
            '.ProseMirror-content')
        textarea.send_keys('i prefer not to')
        self.driver.find_element_by_css_selector(
            'button[type="submit"]').click()

        # Comment index is populated
        index_items = self.driver.find_elements_by_css_selector(
            '.comment-index-item')
        assert_equal(len(index_items), 1)
        assert_in(comment_label, index_items[0].text)

        # Browse to review page
        self.driver.find_element_by_css_selector(
            '.comment-index-review').click()

        # Verify comment in review text
        html = self.driver.find_element_by_css_selector(
            '.comments').get_attribute('innerHTML')
        assert_in(comment_label, html)
        assert_in('i prefer not to', html)

    def test_intro(self):
        """Verify that the intro meta data is visible"""
        self.driver.get(self.test_url + '/preamble/2016_02749/intro')
        html = self.driver.find_element_by_tag_name('html')
        self.assertIn('Addition of a Subsurface Intrusion Component', html)
