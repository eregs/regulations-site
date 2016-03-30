import os
import shutil
import tempfile
from unittest import TestCase

from mock import patch

from regulations.apps import RegulationsConfig


class RegulationsConfigTests(TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    @patch('regulations.apps.get_app_template_dirs')
    def test_precompute_custom_templates(self, get_app_template_dirs):
        """Verify that custom templates are found"""
        get_app_template_dirs.return_value = [self.tmpdir]
        open(os.path.join(self.tmpdir, '123-45-a.html'), 'w').close()
        open(os.path.join(self.tmpdir, 'other.html'), 'w').close()

        RegulationsConfig.precompute_custom_templates()
        self.assertEqual(RegulationsConfig.custom_tpls['123-45-a'],
                         'regulations/custom_nodes/123-45-a.html')
        self.assertEqual(RegulationsConfig.custom_tpls['other'],
                         'regulations/custom_nodes/other.html')
        self.assertFalse('another' in RegulationsConfig.custom_tpls)

    @patch('regulations.apps.get_app_template_dirs')
    def test_precompute_node_type_templates(self, get_app_template_dirs):
        """Verify that node-type templates are found and that a default dict is
        used"""
        get_app_template_dirs.return_value = [self.tmpdir]
        open(os.path.join(self.tmpdir, 'a_new_type.html'), 'w').close()

        RegulationsConfig.precompute_node_type_templates()
        self.assertEqual(RegulationsConfig.node_type_tpls['extract'],
                         'regulations/tree/extract.html')
        self.assertEqual(RegulationsConfig.node_type_tpls['a_new_type'],
                         'regulations/tree/a_new_type.html')
        self.assertEqual(RegulationsConfig.node_type_tpls['something_else'],
                         'regulations/tree/default.html')
