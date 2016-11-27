# -*- coding: utf-8 -*-
import itertools
import logging

from regulations.generator import api_reader
from regulations.generator.generator import DATA_LAYERS
from regulations.generator.layers.tree_builder import roman_nums
from regulations.generator.layers.utils import convert_to_python
from regulations.generator.toc import fetch_toc


logger = logging.getLogger(__name__)


def to_roman(number):
    """ Convert an integer to a roman numeral """
    romans = list(itertools.islice(roman_nums(), 0, number + 1))
    return romans[number - 1]


def get_layer_list(names):
    requested = {name.lower() for name in names.split(',')}
    available = set(DATA_LAYERS.keys())
    return requested & available


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


def layer_names(request):
    """Determine which layers are currently active by looking at the request"""
    if 'layers' in request.GET.keys():
        return get_layer_list(request.GET['layers'])
    else:
        return DATA_LAYERS.keys()


def first_section(reg_part, version):
    """ Use the table of contents for a regulation, to get the label of the
    first section of the regulation. In most regulations, this is -1, but in
    some it's -101. """

    toc = fetch_toc(reg_part, version, flatten=True)
    return toc[0]['section_id']


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
