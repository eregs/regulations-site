# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
from itertools import takewhile

from six.moves import filter, filterfalse

from regulations.generator import node_types
from regulations.generator.layers.layers_applier import LayersApplier
from regulations.generator.layers.internal_citation import (
    InternalCitationLayer)
from regulations.apps import RegulationsConfig
from .link_flattener import flatten_links


class HTMLBuilder(object):
    # @todo simplify this constructor
    def __init__(self, layers=None, diff_applier=None, id_prefix=None,
                 index_prefix=None):
        if layers is None:
            layers = []
        self.layers = layers
        self.tree = None
        self.diff_applier = diff_applier
        self.id_prefix = id_prefix or []
        self.index_prefix = index_prefix or []
        self.preprocess()

    def preprocess(self):
        """Noop. Hook for subclasses"""
        pass

    def generate_html(self):
        if self.diff_applier:
            self.diff_applier.tree_changes(self.tree)
        for layer in self.layers:
            if hasattr(layer, 'preprocess_root'):   # @todo - remove
                layer.preprocess_root(self.tree)
        self.process_node(self.tree, indexes=self.index_prefix)

    def list_level(self, parts, node_type):
        return len(parts) - 2

    def process_node_title(self, node):
        if 'title' in node:
            node['header'] = node['title']
            if self.diff_applier:
                node['header'] = self.diff_applier.apply_diff(
                    node['header'], node['label_id'], component='title')

    @staticmethod
    def is_collapsed(node):
        """A "collapsed" paragraph is one which has no text, immediately
        starting a subparagraph. For example:
        (a)(1) Some text    <- (a) is collapsed
        (a) Some text - (1) Other text   <- (a) is not collapsed
        """
        marker = '({})'.format(node['label'][-1])
        text_without_marker = node['text'].replace(marker, '')
        return node['text'].strip() and not text_without_marker.strip()

    def process_node(self, node, indexes=None):
        """Every node passes through this function on the way to being
        rendered. Importantly, this adds the `marked_up` field, which contains
        the HTML version of node's text (after applying all relevant
        layers) and the `template_name` field, which defines how this node
        should be rendered."""

        node['label_id'] = '-'.join(node['label'])
        self.process_node_title(node)
        node['is_collapsed'] = self.is_collapsed(node)

        node['indexes'] = indexes or []
        node['html_label'] = node_types.to_markup_id(node['label'])
        node['markup_id'] = "-".join(node['html_label'])
        node['full_id'] = "-".join(self.id_prefix + node['html_label'])
        node['tree_level'] = len(node['label']) - 1
        node['human_label'] = self.human_label(node)

        node['list_level'] = self.list_level(node['label'], node['node_type'])

        if len(node['text']):
            if self.diff_applier:
                node['marked_up'] = self.diff_applier.apply_diff(
                    node['text'], node['label_id'])

            layers_applier = LayersApplier()
            for layer in self.layers:
                layers_applier.enqueue_from_list(layer.inline_replacements(
                    node['label_id'], node['text']))

            node['marked_up'] = layers_applier.apply_layers(
                node.get('marked_up', node['text']))
            node['marked_up'] = flatten_links(node['marked_up'])

        for layer in self.layers:
            layer.attach_metadata(node)

        node['template_name'] = RegulationsConfig.custom_tpls.get(
            node['label_id'],
            RegulationsConfig.node_type_tpls[node['node_type'].lower()])

        for idx, child in enumerate(node['children']):
            self.process_node(child, indexes=node['indexes'] + [idx])

    @staticmethod
    def human_label(node):
        """Derive a human-readable description for this node"""
        return '-'.join(node['label'])      # Default


class CFRHTMLBuilder(HTMLBuilder):
    SECTION_NUMBER_REGEX = re.compile(r'(§+)\s+')

    @classmethod
    def section_space(cls, text):
        """ After a section sign, insert a non-breaking space. """
        return cls.SECTION_NUMBER_REGEX.sub(r'\1&nbsp;', text)

    def list_level(self, parts, node_type):
        """ Return the list level and the list type. Overrides"""
        if node_type == node_types.INTERP:
            prefix_length = parts.index('Interp')+1
        elif node_type == node_types.APPENDIX:
            prefix_length = 3
        else:
            prefix_length = 2

        if len(parts) > prefix_length:
            return len(parts) - prefix_length
        return 0

    def process_node_title(self, node):
        """Add space to header. Overrides"""
        super(CFRHTMLBuilder, self).process_node_title(node)
        if 'header' in node:
            node['header'] = self.section_space(node['header'])

    def process_node(self, node, indexes=None):
        """Overrides with custom, additional processing"""
        super(CFRHTMLBuilder, self).process_node(node, indexes=indexes)
        if 'marked_up' in node:
            node['marked_up'] = self.section_space(node['marked_up'])

        if 'TOC' in node:
            for l in node['TOC']:
                l['label'] = self.section_space(l['label'])

        if 'interp' in node and 'markup' in node['interp']:
            node['interp']['markup'] = self.section_space(
                node['interp']['markup'])

        if node['node_type'] == node_types.INTERP:
            self.modify_interp_node(node)

    def modify_interp_node(self, node):
        """Add extra fields which only exist on interp nodes"""
        #   ['105', '22', 'Interp'] => section header
        node['section_header'] = len(node['label']) == 3

        def is_header(child):
            return child['label'][-1] == 'Interp'

        node['header_children'] = list(filter(is_header, node['children']))
        node['par_children'] = list(filterfalse(is_header, node['children']))
        if 'header' in node:
            node['header_markup'] = node['header']
            citation = list(takewhile(lambda p: p != 'Interp',
                                      node['label']))
            for layer in self.layers:
                if (isinstance(layer, InternalCitationLayer)
                        and len(citation) > 2):
                    text = '%s(%s)' % (citation[1], ')('.join(citation[2:]))
                    node['header_markup'] = node['header_markup'].replace(
                        text, layer.render_url(citation, text))

    @staticmethod
    def human_label(node):
        """Derive a human-readable description for this node. Override"""
        return node_types.label_to_text(node['label'], include_marker=True)


class PreambleHTMLBuilder(HTMLBuilder):
    @staticmethod
    def human_label(node):
        """Derive a human-readable description for this node. Override"""
        is_markerless = node_types.MARKERLESS_REGEX.match
        prefix = list(takewhile(lambda l: not is_markerless(l),
                                node['label']))
        if 'intro' in prefix:
            title = node.get('title', '').rstrip(':')
            return 'Intro: ' + title
        elif len(prefix) > 1:
            label = 'Section ' + '.'.join(prefix[1:])
            count = len(node['label']) - len(prefix)
            if count and node.get('indexes'):
                paragraphs = '.'.join(
                    str(idx + 1)
                    for idx in node['indexes'][-count:]
                )
                label += ' Paragraph ' + paragraphs
            return label
        else:
            return 'FR #' + prefix[0]

    def process_node(self, node, indexes=None):
        """Overrides with custom, additional processing"""
        super(PreambleHTMLBuilder, self).process_node(node, indexes=indexes)
        node['accepts_comments'] = True
        node['comments_calledout'] = bool(node.get('title'))

        def not_markerless(l):
            return not node_types.MARKERLESS_REGEX.match(l)

        markers = takewhile(not_markerless, node['label'][:4])
        node['toc_id'] = '-'.join(self.id_prefix + list(markers))


class CFRChangeHTMLBuilder(CFRHTMLBuilder):
    """Generated HTML specifically related to changing CFR data, as displayed
    in a notice. This assumes self.diff_applier is set"""
    def process_node(self, node, indexes=None):
        """Overrides with custom, additional processing"""
        super(CFRHTMLBuilder, self).process_node(node, indexes=indexes)
        label_id = '-'.join(node['label'])
        node['toc_id'] = '-'.join(self.id_prefix + node['label'][:2])
        node['accepts_comments'] = label_id in self.diff_applier.diff
        node['comments_calledout'] = label_id in self.diff_applier.diff

        has_diff = label_id in self.diff_applier.diff
        on_diff_path = tuple(node['label']) in self.diff_paths
        if has_diff:
            node['stars_collapse'] = 'none'
        elif on_diff_path:
            node['stars_collapse'] = 'inline'
        else:
            node['stars_collapse'] = 'full'

    def preprocess(self):
        """Pre-generate all of the "paths" associated with diffs; if there's a
        diff for 111-22-c-4-v, we'd capture
        (111,) (111, 22) (111, 22, c) (111, 22, c, 4) and (111, 22, c, 4, v)"""
        self.diff_paths = set()
        for label_id in self.diff_applier.diff:
            label_parts = tuple(label_id.split('-'))
            path = tuple()
            for part in label_parts:
                path = path + (part,)
                self.diff_paths.add(path)
