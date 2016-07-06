# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import patch
import httpretty
import requests

from regulations.docket import sanitize_fields


class SanitizeFieldsTest(TestCase):
    def setUp(self):
        self.patch_document_fields = patch(
            'regulations.docket.get_document_fields')
        mock_object = self.patch_document_fields.start()
        mock_object.return_value = {
            'required_field': {'maxLength': 10, 'required': True},
            'optional_field': {'maxLength': 10, 'required': False},
        }

    def tearDown(self):
        self.patch_document_fields.stop()

    def test_valid_body(self):
        test_body = {
            "required_field": "Value 1",
            "optional_field": "Value 2"
        }
        valid, message = sanitize_fields(test_body)
        self.assertTrue(valid)

    def test_missing_optional_field(self):
        test_body = {
            "required_field": "Value 1"
        }
        valid, message = sanitize_fields(test_body)
        self.assertTrue(valid)

    def test_missing_required_field(self):
        test_body = {
            "optional_field": "Some value"
        }
        valid, message = sanitize_fields(test_body)
        self.assertFalse(valid)
        self.assertEqual("Field required_field is required", message)

    def test_extra_field(self):
        test_body = {
            "required_field": "Value 1",
            "extra_field": "Value 2"
        }
        valid, message = sanitize_fields(test_body)
        self.assertTrue(valid)
        self.assertTrue("extra_field" not in test_body, "extra_field removed")

    def test_field_too_long(self):
        test_body = {
            "required_field": "Value that exceeds 10 chars",
        }
        valid, message = sanitize_fields(test_body)
        self.assertFalse(valid)
        self.assertEqual("Field required_field exceeds maximum length of 10",
                         message)


class SanitizeFieldsHTTPErrorsTest(TestCase):
    def setUp(self):
        httpretty.enable()

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()

    def test_404(self):
        httpretty.register_uri(httpretty.GET, 'http://example.com', status=404)
        with self.settings(REGS_GOV_API_URL='http://example.com'):
            valid, message = sanitize_fields({'something': 'else'})
        self.assertTrue(valid)

    def test_503(self):
        httpretty.register_uri(httpretty.GET, 'http://example.com', status=503)
        with self.settings(REGS_GOV_API_URL='http://example.com'):
            valid, message = sanitize_fields({'something': 'else'})
        self.assertTrue(valid)

    @patch('regulations.docket.requests.get')
    def test_timeout(self, get):
        get.side_effect = requests.Timeout
        with self.settings(REGS_GOV_API_URL='http://example.com'):
            valid, message = sanitize_fields({'something': 'else'})
        self.assertTrue(valid)
