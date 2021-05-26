import logging

from django.conf import settings
from django.core.cache import caches
import requests


_cache_key = '-'.join
logger = logging.getLogger(__name__)


def _fetch(suffix, params=None):
    """Return a JSON result from either a web API. If not configured
    correctly, throw a warning, but proceed"""
    if not settings.API_BASE:
        logger.error("API_BASE not configured. We won't have data")
        return None

    response = requests.get(settings.API_BASE + suffix, params=params)
    if response.status_code == requests.codes.ok:
        return response.json()
    elif response.status_code == 404:
        logger.warning("404 when fetching %s", settings.API_BASE + suffix)
        return None
    else:
        response.raise_for_status()


class ApiReader(object):
    """ Access the regulations API. Either hit the cache, or if there's a miss,
    hit the API instead and cache the results. """

    def __init__(self):
        self.cache = caches['api_cache']

    def effective_parts(self, date):
        return self._get("v2/{}".format(date))

    def part(self, date, title, part):
        return self._get("v2/{}/title/{}/part/{}".format(date, title, part))

    def toc(self, date, title, part):
        return self._get("v2/{}/title/{}/part/{}/toc".format(date, title, part))

    def regversions(self, title, part):
        return self._get("v2/title/{}/part/{}".format(title, part))

    def search(self, query, **kwargs):
        """Search via the API. Never cache these (that's the duty of the search
        index)"""
        kwargs['q'] = query
        return _fetch('v2/search', kwargs)

    def _get(self, api_suffix, api_params=None):
        """ Retrieve from the cache whenever possible, or get from the API """
        if api_params is None:
            api_params = {}
        cache_key_elements = api_suffix.split('/') + list(sorted(
            element for pair in api_params.items() for element in pair))
        cache_key = _cache_key(cache_key_elements)
        cached = self.cache.get(cache_key)

        if cached is not None:
            return cached
        else:
            element = _fetch(api_suffix, api_params)
            self.cache.set(cache_key, element)
            return element
