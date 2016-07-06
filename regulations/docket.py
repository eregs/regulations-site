import logging

import six
import requests

from django.conf import settings
from django.core.cache import caches

logger = logging.getLogger(__name__)

cache = caches['regs_gov_cache']


def fetch(url, **kwargs):
    kwargs['headers'] = kwargs.get(
        'headers', {'X-Api-Key': settings.REGS_GOV_API_KEY})
    kwargs['timeout'] = kwargs.get('timeout', 10)   # timeout after 10 seconds
    response = requests.get(url, **kwargs)
    if response.status_code != requests.codes.ok:
        response.raise_for_status()
    return response.json()


def get_document_fields(document_id):
    """ Retrieve the field list from the document metadata.
        Use a cache as the data hardly ever changes.
        We ignore the 'general_comment' field as it has special treatment.
    """
    if getattr(settings, 'REGS_GOV_API_MOCK', None):
        return {}
    fields = cache.get(document_id)
    if fields is not None:
        return fields

    metadata = fetch(settings.REGS_GOV_API_URL, params={'D': document_id})
    fields = {
        field['attributeName']: field
        for field in metadata['fieldList']
        if field['attributeName'] != 'general_comment'
    }

    add_picklist_options(fields)
    add_combo_options(fields)

    cache.set(document_id, fields)
    return fields


def safe_get_document_fields(document_id):
    """Like get_document_fields, but returns None on error"""
    try:
        return get_document_fields(document_id)
    except requests.exceptions.RequestException as e:
        logger.warning("Error getting data from regs.gov: %s", e)
        return None


def add_picklist_options(fields):
    """Augment list fields with options. Adds a list of options to each field
    of type "picklist".
    """
    for name, field in fields.items():
        if field['uiControl'] == 'picklist':
            data = fetch(field['lookupUrl'])
            field['options'] = data['list']


def add_combo_options(fields):
    """Augment combo fields with dependency-contingent options. Adds a dict
    mapping contingent values to lists of options to each field of type
    "combo".
    """
    for name, field in fields.items():
        if field['uiControl'] == 'combo':
            field['options'] = {}
            for option in fields[field['dependsOn']]['options']:
                data = fetch(field['lookupUrl'] + option['value'])
                field['options'][option['value']] = data.get('list', [])


def sanitize_fields(body):
    """ Validate fields against the document metadata.
        Remove any extra fields that are not in the document metadata.
        Special treatment for 'assembled_comment' - allow to pass through
        as it holds the text form of the entire submission
    """
    document_fields = safe_get_document_fields(settings.COMMENT_DOCUMENT_ID)
    if document_fields is None:
        return True, ""

    for name, field in six.iteritems(document_fields):
        if field['required'] and name not in body:
            return False, "Field {} is required".format(name)
        if name in body and len(body[name]) > field['maxLength']:
            return False, "Field {} exceeds maximum length of {}".format(
                name, field['maxLength'])

    # Remove extra fields if any, other than 'assembled_comment'
    extra_fields = [field for field in body if field not in document_fields]
    for field in extra_fields:
        if field != 'assembled_comment':
            del body[field]
    return True, ""
