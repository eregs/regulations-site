# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from collections import namedtuple
import logging
import re

from django.core.urlresolvers import reverse

from regulations.generator.toc import fetch_toc
from regulations.views import utils


logger = logging.getLogger(__name__)


class Title(namedtuple('Title', ['full', 'short', 'subtitle'])):
    def __new__(cls, full, short=None, subtitle=None):
        """Adds defaults to constructor"""
        return super(Title, cls).__new__(cls, full, short, subtitle)


class NavItem(namedtuple(
        'NavItem',
        ['url', 'title', 'markup_id', 'children', 'category', 'section_id'])):
    """Shared data structure to represent entries in the table of contents and
    the navigation in the page footer. We may be able to expand this
    standardization more broadly than fr_notices, but let's move one step at a
    time.
    :type title: Title
    :type markup_id: str
    :type children: potentially empty list
    :type category: str or None
    :param str section_id: markup id associated with AJAX and other JS;
        temporary shim so that we can turn off AJAX per NavItem. Defaults to
        copy the markup_id
    """
    def __new__(cls, url, title, markup_id, children=None, category=None,
                section_id=None):
        """Adds defaults to constructor"""
        if children is None:
            children = []
        if section_id is None:
            section_id = markup_id

        return super(NavItem, cls).__new__(
            cls, url, title, markup_id, children, category, section_id)

    # Properties/fns for backwards compatibility

    @property
    def markup_prefix(self):
        return self.title.short

    @property
    def sub_label(self):
        return self.title.subtitle


def _preamble_titles(node):
    """Hack: Split out navigation title and subtitle from a preamble node.
       TODO: Emit these fields in a ToC layer in -parser instead
       :param node: a preamble Node (i.e. dict)
       :return: pair of (title, sub_title) strings"""
    marker = node['label'][-1]
    prefix = '{}. '.format(marker.lower())
    normalized_title = node['title'].lower()
    if normalized_title.startswith(prefix):
        title, subtitle = node['title'].split('. ', 1)
        return Title(node['title'], title, subtitle)
    else:
        return Title(node['title'], marker, node['title'])


def make_preamble_nav(nodes, depth=1, max_depth=3):
    """Generate NavItems specific to a notice's preamble.
    :type nodes: iterable of Node (a dict)
    :param int depth: Current nesting depth of navigation elements
    :param int max_depth: We'll stop processing once we reach a certain depth
    """
    toc = []
    have_titles = [n for n in nodes if n.get('title')]
    for node in have_titles:
        url = reverse('chrome_preamble',
                      kwargs={'paragraphs': '/'.join(node['label'][:2])})
        # Add a hash to a specific section if we're not linking to the
        # top-level entry
        if len(node['label']) > 2:
            url += '#' + '-'.join(node['label'])

        markup_id = '{}-preamble-{}'.format(node['label'][0],
                                            '-'.join(node['label']))

        if 'intro' in node['label'] or depth == max_depth:
            children = []
        else:
            children = make_preamble_nav(
                node.get('children', []),
                depth=depth + 1,
                max_depth=max_depth)

        toc.append(NavItem(
            url=url,
            title=_preamble_titles(node),
            markup_id=markup_id,
            children=children
        ))
    return toc


class CFRChangeBuilder(object):
    """Builds the ToC specific to CFR changes from amendment data. As there is
    some valuable state shared between amendment processing, we store it all
    in an object"""
    def __init__(self):
        """version_info structure: {cfr_part -> {"left": str, "right": str}}
        e.g.  {"111": {"left": "v1", "right": "v2"},
               "222": {"left": "vold", "right": "vnew"}}"""
        self.cfr_title = self.cfr_part = self.section = None
        self.section_titles = {}
        self.toc = []

    def add_cfr_part(self, doc_number, version_info, amendment):
        """While processing an amendment, if it refers to a CFR part which
        hasn't been seen before, we need to perform some accounting, fetching
        related meta data, etc."""
        part = amendment['cfr_part']
        if part not in version_info:
            logger.error("No version info for %s", part)
        elif self.cfr_part is None or self.cfr_part != amendment['cfr_part']:
            meta = utils.regulation_meta(part, version_info[part]['right'])
            flat_toc = fetch_toc(part, version_info[part]['right'],
                                 flatten=True)
            self.section_titles = {
                elt['index'][1]: elt['title']
                for elt in flat_toc if len(elt['index']) == 2}
            self.cfr_part = part
            self.cfr_title = meta.get('cfr_title_number')
            self.section = None

            title = '{} CFR {}'.format(self.cfr_title, part)
            markup_id = '{}-cfr-{}'.format(doc_number, part)
            self.toc.append(NavItem(
                url=reverse('cfr_changes', kwargs={
                    'doc_number': doc_number, 'section': part}),
                title=Title('Authority', title, 'Authority'),
                markup_id=markup_id,
                category=title,
                section_id=''))     # disable AJAX

    _cfr_re = re.compile(r'(§ [\d.]+) (.*)')

    def _change_title(self, section):
        if section not in self.section_titles:
            logger.error("Could not find section title for %s", section)
        title_str = self.section_titles.get(section, '')
        # Hack: Reconstitute node prefix and title
        # TODO: Emit these fields in a ToC layer in -parser instead
        match = self._cfr_re.search(title_str)
        if match:
            return Title(title_str, *match.groups())
        else:
            return Title(title_str, title_str)

    def add_change(self, doc_number, label_parts):
        """While processing an amendment, we will encounter sections we
        haven't seen before -- these will ultimately be ToC entries"""
        change_section = label_parts[1]
        is_subpart = 'Subpart' in label_parts or 'Subjgrp' in label_parts
        if not is_subpart and (self.section is None or
                               self.section != change_section):
            self.section = change_section
            section = '-'.join(label_parts[:2])

            self.toc.append(NavItem(
                url=reverse('cfr_changes', kwargs={
                    'doc_number': doc_number,
                    'section': section}),
                title=self._change_title(change_section),
                markup_id='{}-cfr-{}'.format(doc_number, section),
                category='{} CFR {}'.format(self.cfr_title, self.cfr_part)
            ))


def make_cfr_change_nav(doc_number, version_info, amendments):
    """Soup to nuts conversion from a document number to a table of contents
    list"""
    builder = CFRChangeBuilder()
    for amendment in amendments:
        # Amendments are of the form
        # {'cfr_part': 111, 'instruction': 'text1', 'authority': 'text2'} or
        # {'cfr_part': 111, 'instruction': 'text3',
        #  'changes': [['111-22-c', [data1]], ['other', [data2]]}
        builder.add_cfr_part(doc_number, version_info, amendment)
        for change_label, _ in amendment.get('changes', []):
            builder.add_change(doc_number, change_label.split('-'))
    return builder.toc


def footer(preamble_toc, cfr_toc, full_id):
    """Generate "navigation" context which allows the user to move between
    sections in the footer"""
    items = preamble_toc + cfr_toc
    nav = {'previous': None, 'next': None, 'page_type': 'preamble-section'}
    for idx, item in enumerate(items):
        if item.markup_id == full_id:
            if idx > 0:
                nav['previous'] = items[idx - 1]
            if idx < len(items) - 1:
                nav['next'] = items[idx + 1]
    return nav
