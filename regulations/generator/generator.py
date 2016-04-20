from importlib import import_module
import logging
import re
from threading import Thread

from django.conf import settings

from regulations.generator import api_reader
from regulations.generator.layers.base import LayerBase
from regulations.generator.layers.layers_applier import (
    InlineLayersApplier, ParagraphLayersApplier, SearchReplaceLayersApplier)
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


class LayerCreator(object):
    """ This lets us dynamically load layers by shorthand. """
    LAYERS = _data_layers()

    def __init__(self):
        self.appliers = {
            LayerBase.INLINE: InlineLayersApplier(),
            LayerBase.PARAGRAPH: ParagraphLayersApplier(),
            LayerBase.SEARCH_REPLACE: SearchReplaceLayersApplier()}

        self.api = api_reader.ApiReader()

    def get_layer_json(self, layer_name, doc_type, label_id, version=None):
        """Hit the API to retrieve layer data"""
        return self.api.layer(layer_name, doc_type, label_id, version)

    def add_layers(self, layer_names, doc_type, label_id, sectional=False,
                   version=None):
        """Request a list of layers. As this might spawn multiple HTTP
        requests, we wrap the requests in threads so they can proceed
        concurrently."""
        # This doesn't deal with sectional interpretations yet.
        # we'll have to do that.
        layer_names = set(l for l in layer_names
                          if l.lower() in LayerCreator.LAYERS)
        results = []
        procs = []

        def one_layer(layer_name):
            layer_class = LayerCreator.LAYERS[layer_name]
            api_name = layer_class.data_source
            applier_type = layer_class.layer_type
            layer_json = self.get_layer_json(api_name, doc_type, label_id,
                                             version)
            results.append((api_name, applier_type, layer_class, layer_json))

        #   Spawn threads
        for layer_name in layer_names:
            proc = Thread(target=one_layer, args=(layer_name,))
            procs.append(proc)
            proc.start()

        #   Join them (once their work is done)
        for proc in procs:
            proc.join()

        for api_name, applier_type, layer_class, layer_json in results:
            if layer_json is None:
                logging.warning("No data for %s %s %s %s", api_name, doc_type,
                                label_id, version)
            else:
                layer = layer_class(layer_json)

                if sectional and hasattr(layer, 'sectional'):
                    layer.sectional = sectional
                if hasattr(layer, 'version'):
                    layer.version = version

                self.appliers[applier_type].add_layer(layer)

    def get_appliers(self):
        """ Return the appliers. """
        return (self.appliers[LayerBase.INLINE],
                self.appliers[LayerBase.PARAGRAPH],
                self.appliers[LayerBase.SEARCH_REPLACE])


class DiffLayerCreator(LayerCreator):
    def __init__(self, newer_version):
        super(DiffLayerCreator, self).__init__()
        self.newer_version = newer_version

    def get_layer_json(self, layer_name, doc_type, label_id, version):
        """Diffs contain layer data from _two_ documents, each corresponding
        to one of the versions we're comparing. This data is then combined
        before displaying"""
        older_layer = self.api.layer(layer_name, doc_type, label_id, version)
        newer_layer = self.api.layer(layer_name, doc_type, label_id,
                                     self.newer_version)

        layer_json = dict(newer_layer)  # copy
        layer_json.update(older_layer)  # older layer takes precedence
        return layer_json


def get_regulation(regulation, version):
    """ Get the regulation JSON tree. Manipulate the label a bit for easier
    access in the templates."""
    api = api_reader.ApiReader()
    reg = api.regulation(regulation, version)

    if reg:
        title = reg['title']
        # up till the paren
        match = re.search('part \d+[^\w]*([^\(]*)', title, re.I)
        if match:
            reg['title_clean'] = match.group(1).strip()
        match = re.search('\(regulation (\w+)\)', title, re.I)
        if match:
            reg['reg_letter'] = match.group(1)

        return reg


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
