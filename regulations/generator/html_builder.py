#!/usr/bin/env python
# vim: set fileencoding=utf-8
from __future__ import unicode_literals

import re
from itertools import takewhile

from six.moves import filter, filterfalse

from regulations.generator.node_types import to_markup_id, APPENDIX, INTERP
from regulations.generator.layers.layers_applier import LayersApplier
from regulations.generator.layers.internal_citation import (
    InternalCitationLayer)
from regulations.apps import RegulationsConfig
from .link_flattener import flatten_links


class HTMLBuilder():
    header_regex = re.compile(r'^(§&nbsp;)(\s*\d+\.\d+)(.*)$')
    section_number_regex = re.compile(r'(§+)\s+')

    def __init__(
            self, inline_applier, p_applier,
            search_applier, diff_applier=None):
        self.markup = u''
        self.sections = None
        self.tree = None
        self.inline_applier = inline_applier
        self.p_applier = p_applier
        self.search_applier = search_applier
        self.diff_applier = diff_applier

    def generate_html(self):
        if self.diff_applier:
            self.diff_applier.tree_changes(self.tree)
        for layer in self.p_applier.layers.values():
            if hasattr(layer, 'preprocess_root'):   # @todo - remove
                layer.preprocess_root(self.tree)
        self.process_node(self.tree)

    def parse_doc_title(self, reg_title):
        match = re.search(r"[(].+[)]$", reg_title)
        if match:
            return match.group(0)

    @staticmethod
    def section_space(text):
        """ After a section sign, insert a non-breaking space. """
        return HTMLBuilder.section_number_regex.sub(r'\1&nbsp;', text)

    def list_level(self, parts, node_type):
        """ Return the list level and the list type. """
        if node_type == INTERP:
            prefix_length = parts.index('Interp')+1
        elif node_type == APPENDIX:
            prefix_length = 3
        else:
            prefix_length = 2

        if len(parts) > prefix_length:
            return len(parts) - prefix_length
        return 0

    def process_node_title(self, node):
        if 'title' in node:
            node['header'] = node['title']
            if self.diff_applier:
                node['header'] = self.diff_applier.apply_diff(
                    node['header'], node['label_id'], component='title')

            node['header'] = self.section_space(node['header'])

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

    def process_node(self, node):
        """Every node passes through this function on the way to being
        rendered. Importantly, this adds the `marked_up` field, which contains
        the HTML version of node's text (after applying all relevant
        layers) and the `template_name` field, which defines how this node
        should be rendered."""

        node['label_id'] = '-'.join(node['label'])
        self.process_node_title(node)
        node['is_collapsed'] = self.is_collapsed(node)

        node['html_label'] = to_markup_id(node['label'])
        node['markup_id'] = "-".join(node['html_label'])
        node['tree_level'] = len(node['label']) - 1

        list_level = self.list_level(node['label'], node['node_type'])

        node['list_level'] = list_level

        if len(node['text']):
            inline_elements = self.inline_applier.get_layer_pairs(
                node['label_id'], node['text'])
            search_elements = self.search_applier.get_layer_pairs(
                node['label_id'])

            if self.diff_applier:
                node['marked_up'] = self.diff_applier.apply_diff(
                    node['text'], node['label_id'])

            layers_applier = LayersApplier()
            layers_applier.enqueue_from_list(inline_elements)
            layers_applier.enqueue_from_list(search_elements)

            node['marked_up'] = layers_applier.apply_layers(
                node.get('marked_up', node['text']))
            node['marked_up'] = self.section_space(node['marked_up'])
            node['marked_up'] = flatten_links(node['marked_up'])

        node = self.p_applier.apply_layers(node)

        node['template_name'] = RegulationsConfig.custom_tpls.get(
            node['label_id'],
            RegulationsConfig.node_type_tpls[node['node_type'].lower()])

        if 'TOC' in node:
            for l in node['TOC']:
                l['label'] = self.section_space(l['label'])

        if 'interp' in node and 'markup' in node['interp']:
            node['interp']['markup'] = self.section_space(
                node['interp']['markup'])

        if node['node_type'] == INTERP:
            self.modify_interp_node(node)

        for c in node['children']:
            self.process_node(c)

    def modify_interp_node(self, node):
        """Add extra fields which only exist on interp nodes"""
        #   ['105', '22', 'Interp'] => section header
        node['section_header'] = len(node['label']) == 3

        is_header = lambda child: child['label'][-1] == 'Interp'
        node['header_children'] = list(filter(is_header, node['children']))
        node['par_children'] = list(filterfalse(is_header, node['children']))
        if 'header' in node:
            node['header_markup'] = node['header']
            citation = list(takewhile(lambda p: p != 'Interp',
                                      node['label']))
            icl = self.inline_applier.layers.get(
                InternalCitationLayer.shorthand)
            if icl and len(citation) > 2:
                text = '%s(%s)' % (citation[1], ')('.join(citation[2:]))
                node['header_markup'] = node['header_markup'].replace(
                    text, icl.render_url(citation, text))

    def get_title(self):
        titles = {
            'part': self.tree['label'][0],
            'reg_name': ''
        }
        reg_title = self.parse_doc_title(self.tree['title'])
        if reg_title:
            titles['reg_name'] = reg_title
        return titles
