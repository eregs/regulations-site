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
        'NavItem', ['url', 'title', 'section_id', 'children', 'divider'])):
    """Shared data structure to represent entries in the table of contents and
    the navigation in the page footer. We may be able to expand this
    standardization more broadly than fr_notices, but let's move one step at a
    time.
    :type title: Title
    :type section_id: str or None
    :type children: potentially empty list
    :type divider: str or None
    """
    def __new__(cls, url, title, section_id=None, children=None, divider=None):
        """Adds defaults to constructor"""
        if children is None:
            children = []

        return super(NavItem, cls).__new__(cls, url, title, section_id,
                                           children, divider)

    # Properties/fns for backwards compatibility

    @property
    def markup_prefix(self):
        return self.title.short

    @property
    def sub_label(self):
        return self.title.subtitle

    def match_ids(self, ids):
        return self.section_id == ids.get('full_id')

    def to_nav_item(self):
        return self


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
    intro_subheader = depth == 2 and any('intro' in n['label'] for n in nodes)
    if depth > max_depth or intro_subheader:
        return toc

    have_titles = [n for n in nodes if n.get('title')]
    for node in have_titles:
        url = reverse('chrome_preamble',
                      kwargs={'paragraphs': '/'.join(node['label'][:2])})
        # Add a hash to a specific section if we're not linking to the
        # top-level entry
        if len(node['label']) > 2:
            url += '#' + '-'.join(node['label'])

        section_id = '{}-preamble-{}'.format(node['label'][0],
                                             '-'.join(node['label']))

        toc.append(NavItem(
            url=url,
            title=_preamble_titles(node),
            section_id=section_id,
            children=make_preamble_nav(
                node.get('children', []),
                depth=depth + 1,
                max_depth=max_depth,
            )
        ))
    return toc


class ToCPart(namedtuple('ToCPart',
              ['title', 'part', 'name', 'authority_url', 'sections'])):
    def to_nav_item(self):
        title = '{} CFR {}'.format(self.title, self.part)
        return NavItem(
            url=self.authority_url,
            title=Title(title, title, 'Authority')
        )

    def match_ids(self, ids):
        return self.part == ids.get('part') and ids.get('section') is None


class ToCSect(namedtuple('ToCSect',
              ['part', 'section', 'url', 'title', 'full_id'])):
    cfr_re = re.compile(r'(§ [\d.]+) (.*)')

    def to_nav_item(self):
        # Hack: Reconstitute node prefix and title
        # TODO: Emit these fields in a ToC layer in -parser instead
        match = self.cfr_re.search(self.title)
        if match:
            prefix, label = match.groups()
        else:
            prefix, label = self.title, None
        return NavItem(
            url=self.url,
            title=Title(self.title, prefix, label),
            section_id=self.full_id,
        )

    def match_ids(self, ids):
        return (
            self.part == ids.get('part') and
            ids.get('section') == self.section
        )


class CFRChangeBuilder(object):
    """Builds the ToC specific to CFR changes from amendment data. As there is
    some valuable state shared between amendment processing, we store it all
    in an object"""
    def __init__(self, doc_number, version_info):
        """version_info structure: {cfr_part -> {"left": str, "right": str}}
        e.g.  {"111": {"left": "v1", "right": "v2"},
               "222": {"left": "vold", "right": "vnew"}}"""
        self.current_part = None
        self.current_section = None
        self.section_titles = {}
        self.toc = []
        self.doc_number = doc_number
        self.version_info = version_info

    def add_amendment(self, amendment):
        """Process a single amendment, of the form
        {'cfr_part': 111, 'instruction': 'text1', 'authority': 'text2'} or
        {'cfr_part': 111, 'instruction': 'text3',
         'changes': [['111-22-c', [data1]], ['other', [data2]]}"""
        if (self.current_part is None or
                self.current_part.part != amendment['cfr_part']):
            self.new_cfr_part(amendment)

        changes = amendment.get('changes', [])
        if isinstance(changes, dict):
            changes = changes.items()
        for change_label, _ in changes:
            self.add_change(change_label.split('-'))

    def new_cfr_part(self, amendment):
        """While processing an amendment, if it refers to a CFR part which
        hasn't been seen before, we need to perform some accounting, fetching
        related meta data, etc."""
        part = amendment['cfr_part']
        if part not in self.version_info:
            logger.warning("No version info for %s", part)
        else:
            meta = utils.regulation_meta(part,
                                         self.version_info[part]['right'])
            flat_toc = fetch_toc(part, self.version_info[part]['right'],
                                 flatten=True)
            self.section_titles = {
                elt['index'][1]: elt['title']
                for elt in flat_toc if len(elt['index']) == 2}
            self.current_part = ToCPart(
                title=meta.get('cfr_title_number'), part=part,
                name=meta.get('statutory_name'), sections=[],
                authority_url=reverse('cfr_changes', kwargs={
                    'doc_number': self.doc_number, 'section': part}))
            self.current_section = None
            self.toc.append(self.current_part)

    def add_change(self, label_parts):
        """While processing an amendment, we will encounter sections we
        haven't seen before -- these will ultimately be ToC entries"""
        change_section = label_parts[1]
        is_subpart = 'Subpart' in label_parts or 'Subjgrp' in label_parts
        if not is_subpart and (self.current_section is None or
                               self.current_section.section != change_section):

            section = '-'.join(label_parts[:2])
            self.current_section = ToCSect(
                part=self.current_part.part,
                section=change_section,
                title=self.section_titles.get(change_section),
                full_id='{}-cfr-{}'.format(self.doc_number, section),
                url=reverse('cfr_changes', kwargs={
                    'doc_number': self.doc_number,
                    'section': section}))
            self.current_part.sections.append(self.current_section)

    @classmethod
    def for_notice(cls, doc_number, versions, amendments):
        """Soup to nuts conversion from a document number to a table of
        contents list"""
        builder = cls(doc_number, versions)
        for amendment in amendments:
            builder.add_amendment(amendment)
        return builder.toc
