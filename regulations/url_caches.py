from datetime import date

from django.conf import settings
from django.utils.decorators import decorator_from_middleware_with_args
from django.views.decorators.cache import cache_page
from django.middleware.cache import CacheMiddleware


lt_cache = cache_page(settings.CACHES['eregs_longterm_cache']['TIMEOUT'],
                      cache='eregs_longterm_cache')


class DailyCacheMiddleware(CacheMiddleware):
    """Like the cache middleware, but always expires at midnight"""
    @property
    def key_prefix(self):
        return date.today().isoformat() + '/' + (self.__key_prefix or '')

    @key_prefix.setter
    def key_prefix(self, value):
        self.__key_prefix = value


daily_cache = decorator_from_middleware_with_args(DailyCacheMiddleware)(
    cache_timeout=settings.CACHES['eregs_longterm_cache']['TIMEOUT'],
    cache_alias='eregs_longterm_cache')
