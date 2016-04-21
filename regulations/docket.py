from collections import namedtuple
import logging

import six
import requests

from django.conf import settings
from django.core.cache import caches

Field = namedtuple('Field', 'max_length, required')

logger = logging.getLogger(__name__)


def get_document_metadata(document_id):
    """ Retrieve document metadata from regulations.gov. """
    logger.debug("Getting docket metadata")
    response = requests.get(
        settings.REGS_GOV_API_URL,
        params={'D': document_id},
        headers={'X-Api-Key': settings.REGS_GOV_API_KEY}
    )
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        logger.error("Failed to lookup regulations.gov: {}",
                     response.status_code, response.text)
        response.raise_for_status()


def get_document_fields(document_id):
    """ Retrieve the field list from the document metadata.
        Use a cache as the data hardly ever changes.
        We ignore the 'general_comment' field as it has special treatment.
    """
    cache = caches['regs_gov_cache']
    cache_key = document_id
    fields = cache.get(cache_key)

    if fields is None:
        document_metadata = get_document_metadata(document_id)
        fields = {
            field['attributeName']: Field(field['maxLength'],
                                          field['required'])
            for field in document_metadata['fieldList']
            if field['attributeName'] != 'general_comment'
        }
        cache.set(cache_key, fields)
    return fields


def sanitize_fields(body):
    """ Validate fields against the document metadata.
        Remove any extra fields that are not in the document metadata.
        Specila treatment for 'assembled_comment' - allow to pass through
        as it holds the text form of the entire submission
    """
    document_fields = get_document_fields(settings.COMMENT_DOCUMENT_ID)
    for name, field in six.iteritems(document_fields):
        if field.required and name not in body:
            return False, "Field {} is required".format(name)
        if name in body and len(body[name]) > field.max_length:
            return False, "Field {} exceeds expected length of {}".format(
                name, field.max_length)

    # Remove extra fields if any, other than 'assembled_comment'
    extra_fields = [field for field in body if field not in document_fields]
    for field in extra_fields:
        if field != 'assembled_comment':
            del body[field]
    return True, ""
