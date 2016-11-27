# -*- coding: utf-8 -*-
from collections import namedtuple

import six
from django.core.urlresolvers import reverse

from regulations.generator import generator
from regulations.generator.html_builder import CFRHTMLBuilder
from regulations.generator.layers.toc_applier import TableOfContentsLayer
from regulations.generator.node_types import EMPTYPART, REGTEXT
from regulations.generator.section_url import SectionUrl
from regulations.generator.sidebar.diff_help import DiffHelp
from regulations.generator.toc import fetch_toc
from regulations.views import error_handling, utils
from regulations.views.chrome import ChromeView
from regulations.views.partial import PartialView


class Versions(namedtuple('Versions', ['older', 'newer', 'return_to'])):
    def __new__(cls, older, newer, return_to=None):
        if return_to is None:
            return_to = older
        return super(Versions, cls).__new__(cls, older, newer, return_to)


class PartialSectionDiffView(PartialView):
    """ A diff view of a partial section. """
    template_name = 'regulations/regulation-content.html'

    def get(self, request, *args, **kwargs):
        """ Override GET so that we can catch and propagate any errors. """

        try:
            return super(PartialSectionDiffView, self).get(request, *args,
                                                           **kwargs)
        except error_handling.MissingContentException:
            return error_handling.handle_generic_404(request)

    def footer_nav(self, label, toc, versions):
        nav = {}
        for idx, toc_entry in enumerate(toc):
            if toc_entry['section_id'] != label:
                continue

            if idx > 0:
                nav['previous'] = toc[idx - 1]

            if idx < len(toc) - 1:
                nav['next'] = toc[idx + 1]

        # Add the url
        for entry in nav.values():
            entry['url'] = reverse_chrome_diff_view(
                entry['section_id'], *versions)

        nav['page_type'] = 'diff'

        return nav

    def get_context_data(self, **kwargs):
        # We don't want to run the content data of PartialView -- it assumes
        # we will be applying layers
        context = super(PartialView, self).get_context_data(**kwargs)

        label_id = context['label_id']
        versions = Versions(context['version'], context['newer_version'],
                            self.request.GET.get('from_version'))

        tree = generator.get_tree_paragraph(label_id, versions.older)

        if tree is None:
            # TODO We need a more complicated check here to see if the diffs
            # add the requested section. If not -> 404
            tree = {}

        diff_applier = generator.get_diff_applier(
            label_id, versions.older, versions.newer)
        if diff_applier is None:
            raise error_handling.MissingContentException()
        layers = list(generator.diff_layers(versions, label_id))

        builder = CFRHTMLBuilder(layers, diff_applier)
        builder.tree = tree
        builder.generate_html()

        child_of_root = builder.tree
        if builder.tree['node_type'] == REGTEXT:
            child_of_root = {
                'node_type': EMPTYPART,
                'children': [builder.tree]}
        context['tree'] = {'children': [child_of_root]}
        context['markup_page_type'] = 'diff'

        regpart = label_id.split('-')[0]
        old_toc = fetch_toc(regpart, versions.older)
        diff = generator.get_diff_json(regpart, versions.older, versions.newer)
        context['TOC'] = diff_toc(versions, old_toc, diff)
        context['navigation'] = self.footer_nav(
            label_id, context['TOC'], versions)
        return context


class ChromeSectionDiffView(ChromeView):
    """Search results with chrome"""
    template_name = 'regulations/diff-chrome.html'
    partial_class = PartialSectionDiffView
    sidebar_components = [DiffHelp]

    def check_tree(self, context):
        pass    # The tree may or may not exist in the particular version

    def add_diff_content(self, context):
        context['from_version'] = self.request.GET.get(
            'from_version', context['version'])
        context['left_version'] = context['version']
        context['right_version'] = \
            context['main_content_context']['newer_version']
        from_version = self.request.GET.get('from_version', context['version'])

        context['TOC'] = context['main_content_context']['TOC']

        #   Add reference to the first subterp, so we know how to redirect
        toc = fetch_toc(context['label_id'].split('-')[0], from_version)
        for entry in toc:
            if entry.get('is_supplement') and entry.get('sub_toc'):
                el = entry['sub_toc'][0]
                el['url'] = SectionUrl().of(
                    el['index'], from_version,
                    self.partial_class.sectional_links)
                context['first_subterp'] = el
        return context

    def add_main_content(self, context):
        super(ChromeSectionDiffView, self).add_main_content(context)
        return self.add_diff_content(context)


def reverse_chrome_diff_view(sect_id, left_ver, right_ver, from_version):
    """ Reverse the URL for a chromed diff view. """

    diff_url = reverse(
        'chrome_section_diff_view',
        args=(sect_id, left_ver, right_ver))
    diff_url += '?from_version=%s' % from_version
    return diff_url


def extract_sections(toc):
    compiled_toc = []
    for i in toc:
        if 'Subpart' in i['index'] or 'Subjgrp' in i['index']:
            compiled_toc.extend(i['sub_toc'])
        else:
            compiled_toc.append(i)
    return compiled_toc


def diff_toc(versions, old_toc, diff):
    # We work around Subparts in the TOC for now.
    compiled_toc = extract_sections(old_toc)

    for node in (v['node'] for v in diff.values() if v['op'] == 'added'):
        if len(node['label']) == 2 and node['title']:
            element = {
                'label': node['title'],
                'index': node['label'],
                'section_id': '-'.join(node['label']),
                'op': 'added'
            }
            data = {'index': node['label'], 'title': node['title']}
            TableOfContentsLayer.section(element, data)
            TableOfContentsLayer.appendix_supplement(element, data)
            compiled_toc.append(element)

    modified, deleted = modified_deleted_sections(diff)
    for el in compiled_toc:
        if 'Subpart' not in el['index'] and 'Subjgrp' not in el['index']:
            el['url'] = reverse_chrome_diff_view(el['section_id'], *versions)
        # Deleted first, lest deletions in paragraphs affect the section
        if tuple(el['index']) in deleted and 'op' not in el:
            el['op'] = 'deleted'
        if tuple(el['index']) in modified and 'op' not in el:
            el['op'] = 'modified'

    return sorted(compiled_toc, key=normalize_toc)


def normalize_toc(toc_element):
    """Return a sorting order for a TOC element, primarily based on the
    index, and the type of content. General order is regulation text,
    appendices, then interpretations."""

    sortable_index = tuple(utils.make_sortable(l)
                           for l in toc_element['index'])
    if toc_element.get('is_section'):
        return (0,) + sortable_index
    elif toc_element.get('is_appendix'):
        return (1,) + sortable_index
    elif toc_element.get('is_supplement'):
        return (2,) + sortable_index
    else:
        return (3,) + sortable_index


def modified_deleted_sections(diff):
    modified, deleted = set(), set()
    for label, diff_value in six.iteritems(diff):
        label = tuple(label.split('-'))
        if 'Interp' in label:
            section_label = (label[0], 'Interp')
        else:
            section_label = tuple(label[:2])

        # Whole section was deleted
        if diff_value['op'] == 'deleted' and label == section_label:
            deleted.add(section_label)
        # Whole section added/modified or paragraph added/deleted/modified
        else:
            modified.add(section_label)
    return modified, deleted
