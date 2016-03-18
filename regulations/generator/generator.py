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
from regulations.generator.html_builder import HTMLBuilder
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

    def get_layer_json(self, api_name, regulation, version):
        """ Hit the API to retrieve the regulation JSON. """
        return self.api.layer(api_name, regulation, version)

    def add_layer(self, layer_name, regulation, version, sectional=False):
        """ Add a normal layer (no special handling required) to the applier.
        """

        if layer_name.lower() in LayerCreator.LAYERS:
            layer_class = LayerCreator.LAYERS[layer_name]
            api_name = layer_class.data_source
            applier_type = layer_class.layer_type
            layer_json = self.get_layer_json(api_name, regulation, version)
            if layer_json is None:
                logging.warning("No data for %s/%s/%s"
                                % (api_name, regulation, version))
            else:
                layer = layer_class(layer_json)

                if sectional and hasattr(layer, 'sectional'):
                    layer.sectional = sectional
                if hasattr(layer, 'version'):
                    layer.version = version

                self.appliers[applier_type].add_layer(layer)

    def add_layers(self, layer_names, regulation, version, sectional=False):
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
            layer_json = self.get_layer_json(api_name, regulation, version)
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
                logging.warning("No data for %s/%s/%s"
                                % (api_name, regulation, version))
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

    @staticmethod
    def combine_layer_versions(older_layer, newer_layer):
        """ Create a new layer by taking all the nodes from the older
        layer, and adding to the all the new nodes from the newer layer. """

        combined_layer = {}

        for n in older_layer:
            combined_layer[n] = older_layer[n]

        for n in newer_layer:
            if n not in combined_layer:
                combined_layer[n] = newer_layer[n]

        return combined_layer

    def get_layer_json(self, api_name, regulation, version):
        older_layer = self.api.layer(api_name, regulation, version)
        newer_layer = self.api.layer(api_name, regulation, self.newer_version)

        layer_json = self.combine_layer_versions(older_layer, newer_layer)
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


def get_builder(regulation, version, inline_applier, p_applier, s_applier):
    """ Returns an HTML builder with the appliers, and the regulation tree. """
    builder = HTMLBuilder(inline_applier, p_applier, s_applier)
    builder.tree = get_regulation(regulation, version)
    return builder


def get_all_notices():
    api = api_reader.ApiReader()
    return notices.fetch_all(api)


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
