from concurrent.futures import ThreadPoolExecutor
from importlib import import_module

from django.conf import settings

from regulations.generator import api_reader
from regulations.generator.layers.diff_applier import DiffApplier
from regulations.generator import notices


def _data_layers():
    """Index all configured data layers by their "shorthand". This doesn't
    have any error checking -- it'll explode if configured improperly"""
    layers = {}
    for class_path in settings.DATA_LAYERS:
        module, class_name = class_path.rsplit('.', 1)
        klass = getattr(import_module(module), class_name)
        layers[klass.shorthand] = klass
    return layers


DATA_LAYERS = _data_layers()


def generate_layers(layer_names, fetch_fn, **layer_attrs):
    """Return the three LayerApplier classes, populated with the appropriate
    layer data. Fetches this data in parallel.
    :param layer_names: list of layer short names
    :param fetch_fn: a function, which, when given a layer short name, returns
        the corresponding layer data
    :param layer_attrs: any other attributes to set on the layer object
    """
    layer_names = [l for l in layer_names if l in DATA_LAYERS]

    with ThreadPoolExecutor(max_workers=len(layer_names)) as executor:
        result_data = executor.map(fetch_fn, layer_names)

    for layer_name, layer_json in zip(layer_names, result_data):
        if layer_json is not None:
            layer_class = DATA_LAYERS[layer_name]
            layer = layer_class(layer_json)
            for attr_name, attr_val in layer_attrs.items():
                setattr(layer, attr_name, attr_val)

            yield layer


def layers(layer_names, doc_type, label_id, sectional=False, version=None):
    """Generate the three layer appliers for most situations"""
    def layer_fn(layer_name):
        api_layer_name = DATA_LAYERS[layer_name].data_source
        reader = api_reader.ApiReader()
        return reader.layer(api_layer_name, doc_type, label_id, version)
    return generate_layers(layer_names, layer_fn, version=version,
                           sectional=sectional)


def diff_layers(versions, label_id):
    """Generate the three layer appliers for diffs, which combine two sources
    of layer data"""
    def layer_fn(layer_name):
        api_layer_name = DATA_LAYERS[layer_name].data_source
        reader = api_reader.ApiReader()
        older_layer = reader.layer(api_layer_name, 'cfr', label_id,
                                   versions.older)
        newer_layer = reader.layer(api_layer_name, 'cfr', label_id,
                                   versions.newer)
        older_layer = older_layer or {}
        newer_layer = newer_layer or {}

        layer_json = dict(newer_layer)  # copy
        layer_json.update(older_layer)  # older layer takes precedence
        return layer_json
    layer_names = [
        'graphics', 'paragraph', 'keyterms', 'defined', 'formatting',
        'marker-hiding', 'marker-info'
    ]
    return generate_layers(layer_names, layer_fn, version=versions.older)


def get_tree_paragraph(paragraph_id, version):
    """Get a single level of the regulation tree."""
    api = api_reader.ApiReader()
    return api.regulation(paragraph_id, version)


def get_notice(document_number):
    """ Get a the data from a particular notice, given the Federal Register
    document number. """

    api = api_reader.ApiReader()
    return api.notice(document_number)


def get_sxs(label_id, notice, fr_page=None):
    """ Given a paragraph label_id, find the sxs analysis for that paragraph if
    it exists and has content. fr_page is used to distinguish between
    multiple analyses in the same notice."""

    all_sxs = notice['section_by_section']
    relevant_sxs = notices.find_label_in_sxs(all_sxs, label_id, fr_page)

    return relevant_sxs


def get_diff_json(regulation, older, newer):
    api = api_reader.ApiReader()
    return api.diff(regulation, older, newer)


def get_diff_applier(label_id, older, newer):
    regulation = label_id.split('-')[0]
    diff_json = get_diff_json(regulation, older, newer)
    if diff_json is not None:
        return DiffApplier(diff_json, label_id)
