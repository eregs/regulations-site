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

    def all_regulations_versions(self):
        """ Get all versions, for all regulations. """
        return self._get('regulation')

    def regversions(self, label):
        return self._get('regulation/{}'.format(label))

    def cache_root_and_interps(self, reg_tree, version, is_root=True):
        """We will re-use the root tree at multiple points during page
        rendering, so cache it now. If caching an interpretation, also store
        child interpretations with titles (so that, when rendering slide-down
        interpretations, we don't perform additional fetches)"""
        if is_root or reg_tree.get('title'):
            tree_id = '-'.join(reg_tree['label'])
            cache_key = _cache_key(['regulation', tree_id, version])
            self.cache.set(cache_key, reg_tree)

        for child in reg_tree['children']:
            if child.get('node_type') == 'interp':
                self.cache_root_and_interps(child, version, False)

    def regulation(self, label, version):
        cache_key = _cache_key(['regulation', label, version])
        cached = self.cache.get(cache_key)

        if cached is not None:
            return cached
        else:
            regulation = _fetch('regulation/{}/{}'.format(label, version))
            # Add the tree to the cache
            if regulation:
                self.cache_root_and_interps(regulation, version)
                return regulation

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

    def layer(self, layer_name, doc_type, label_id, version=None):
        """When retrieving layer data, we cheat a bit -- we always retrieve
        layer data corresponding to the "root" of the document, rather than
        only a subnode. We also must convert to the API format, where any
        version information is prefixed to doc_id"""
        root = label_id.split('-')[0]
        if version is None:
            doc_id = root
        else:
            doc_id = '{}/{}'.format(version, root)
        result = self._get(
            'layer/{}/{}/{}'.format(layer_name, doc_type, doc_id))
        # To remove - also try the old format for CFR layers; the API may not
        # have been updated
        if result is None and doc_type == 'cfr':
            result = self._get(
                'layer/{}/{}/{}'.format(layer_name, root, version))
        return result

    def diff(self, label, older, newer):
        """ End point for diffs. """
        return self._get("diff/{}/{}/{}".format(label, older, newer))

    def notices(self, part=None):
        """ End point for notice searching. Right now just a list. """
        params = None
        if part:
            params = {'part': part}
        return self._get('notice', params)

    def notice(self, fr_document_number):
        """ End point for retrieving a single notice. """
        return self._get('notice/{}'.format(fr_document_number))

    def search(self, query, doc_type='cfr', version=None, regulation=None,
               **kwargs):
        """Search via the API. Never cache these (that's the duty of the search
        index)"""
        params = {'q': query}
        if version:
            params['version'] = version
        if regulation:
            params['regulation'] = regulation
        params.update(kwargs)
        return _fetch('search/{}'.format(doc_type), params)

    def preamble(self, doc_number):
        return self._get('preamble/{}'.format(doc_number))
