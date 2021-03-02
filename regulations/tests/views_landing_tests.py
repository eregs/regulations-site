from unittest import TestCase
from mock import patch

from regulations.generator.versions import Timeline, get_versions


class LandingViewTest(TestCase):
    @patch('regulations.generator.versions.fetch_grouped_history')
    def test_get_versions(self, fetch_grouped_history):
        fetch_grouped_history.return_value = [
            {'timeline': Timeline.future, 'version': 'a'},
            {'timeline': Timeline.present, 'version': 'b'}]
        current_ver, next_ver = get_versions('204')
        self.assertEqual({'timeline': Timeline.present, 'version': 'b'},
                         current_ver)
        self.assertEqual({'timeline': Timeline.future, 'version': 'a'},
                         next_ver)

    @patch('regulations.generator.versions.fetch_grouped_history')
    def test_get_versions_no_next(self, fetch_grouped_history):
        fetch_grouped_history.return_value = [
            {'timeline': Timeline.present, 'version': 'b'}]
        current_ver, next_ver = get_versions('204')
        self.assertEqual({'timeline': Timeline.present, 'version': 'b'},
                         current_ver)
        self.assertEqual(None, next_ver)
