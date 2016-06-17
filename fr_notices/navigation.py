from collections import namedtuple

from django.core.urlresolvers import reverse


class Title(namedtuple('Title', ['full', 'short', 'subtitle'])):
    def __new__(cls, full, short=None, subtitle=None):
        """Adds defaults to constructor"""
        return super(Title, cls).__new__(cls, full, short, subtitle)


class NavItem(namedtuple('NavItem',
                         ['url', 'title', 'section_id', 'children'])):
    """Shared data structure to represent entries in the table of contents and
    the navigation in the page footer. We may be able to expand this
    standardization more broadly than fr_notices, but let's move one step at a
    time.
    :type title: Title
    :type section_id: str or None
    :type children: potentially empty list
    """
    def __new__(cls, url, title, section_id=None, children=None):
        """Adds defaults to constructor"""
        if children is None:
            children = []

        return super(NavItem, cls).__new__(cls, url, title, section_id,
                                           children)

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
