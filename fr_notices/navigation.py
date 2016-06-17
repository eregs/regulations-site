from collections import namedtuple


class NavItem(namedtuple(
        'NavItem', ['url', 'title', 'sub_title', 'section_id', 'children'])):
    """Shared data structure to represent entries in the table of contents and
    the navigation in the page footer. We may be able to expand this
    standardization more broadly than fr_notices, but let's move one step at a
    time.
    :type sub_title: str or None
    :type section_id: str or None
    :type children: potentially empty list
    """
    def __new__(cls, url, title, sub_title=None, section_id=None,
                children=None):
        """Adds defaults to constructor"""
        if children is None:
            children = []
        return super(NavItem, cls).__new__(cls, url, title, sub_title,
                                           section_id, children)

    # Properties for backwards compatibility

    @property
    def markup_prefix(self):
        return self.title

    @property
    def sub_label(self):
        return self.sub_title
