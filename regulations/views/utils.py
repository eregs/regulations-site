# -*- coding: utf-8 -*-
import itertools
import logging

from regulations.views.errors import NotInSubpart
from regulations.generator import api_reader
from regulations.generator.utils import roman_nums, convert_to_python
from regulations.generator.toc import fetch_toc


logger = logging.getLogger(__name__)


def to_roman(number):
    """ Convert an integer to a roman numeral """
    romans = list(itertools.islice(roman_nums(), 0, number + 1))
    return romans[number - 1]


def regulation_meta(cfr_part, version):
    """ Return the contents of the meta layer, without using a tree. """
    layer_data = api_reader.ApiReader().layer('meta', 'cfr', cfr_part, version)
    if layer_data is None:
        logger.warning("404 when fetching Meta for %s@%s", cfr_part, version)
        layer_data = {}
    if not layer_data.get(cfr_part):
        logger.warning("Empty meta data for %s@%s. Misparsed?",
                       cfr_part, version)

    meta = {}
    for data in layer_data.get(cfr_part, []):
        meta.update(data)
    return convert_to_python(meta)


def first_section(reg_part, version):
    """ Use the table of contents for a regulation, to get the label of the
    first section of the regulation. In most regulations, this is -1, but in
    some it's -101. """

    toc = fetch_toc(reg_part, version, flatten=True)
    return toc[0]['index'][1]


def first_subpart(reg_part, version):
    toc = fetch_toc(reg_part, version)
    for el in toc:
        if 'Subpart' in el['index']:
            return '-'.join(el['index'][1:])
    return None


def find_subpart(section, toc, subpart=None):
    for el in toc:
        value = None
        if el['index'][1] == section:
            if subpart is None:
                raise NotInSubpart()
            return subpart
        elif 'Subpart' in el['index'] and 'sub_toc' in el:
            value = find_subpart(section, el['sub_toc'], '-'.join(el['index'][1:]))
        elif 'Subjgrp' in el['index'] and 'sub_toc' in el:
            value = find_subpart(section, el['sub_toc'], subpart)

        if value is not None:
            return value

    return None


def find_subpart_first_section(subpart, toc):
    for el in toc:
        if subpart.lower() == '-'.join(el['index'][1:]).lower():
            return el['sub_toc'][0]['index'][1]
    return None


def make_sortable(string):
    """Split a string into components, converting digits into ints so sorting
    works as we would expect"""
    if not string:      # base case
        return tuple()
    elif string[0].isdigit():
        prefix = "".join(itertools.takewhile(lambda c: c.isdigit(), string))
        return (int(prefix),) + make_sortable(string[len(prefix):])
    else:
        prefix = "".join(itertools.takewhile(lambda c: not c.isdigit(),
                                             string))
        return (prefix,) + make_sortable(string[len(prefix):])
