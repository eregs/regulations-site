from datetime import date

from django.http import HttpResponse
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils.decorators import decorator_from_middleware_with_args
from mock import Mock, patch

from regulations import url_caches


class UrlCachesTests(TestCase):
    @patch('regulations.url_caches.date')
    def test_daily_cache(self, patched_date):
        """Cache should be consistent within a day but not between days"""
        fn = Mock(return_value=HttpResponse('response'))
        request = RequestFactory().get('a-path')

        mock_caches = {'example': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
        with self.settings(CACHES=mock_caches):
            daily_cache = decorator_from_middleware_with_args(
                url_caches.DailyCacheMiddleware)(cache_alias='example')
            wrapped_fn = daily_cache(fn)

        patched_date.today.return_value = date(2010, 10, 10)
        self.assertEqual(fn.call_count, 0)
        wrapped_fn(request)
        self.assertEqual(fn.call_count, 1)
        wrapped_fn(request)
        self.assertEqual(fn.call_count, 1)

        patched_date.today.return_value = date(2010, 10, 11)
        wrapped_fn(request)
        self.assertEqual(fn.call_count, 2)
        wrapped_fn(request)
        self.assertEqual(fn.call_count, 2)
