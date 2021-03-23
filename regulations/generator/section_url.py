from django.urls import reverse, NoReverseMatch

from regulations.generator.node_types import to_markup_id


class SectionUrl(object):
    """With few exceptions, users are expected to browse the regulation by
    traversing regtext sections, appendices, and subterps (split
    interpretations). This object will deduce, from a version and citation,
    to which section/appendix/subterp to link, a task greatly complicated by
    subterps. Importantly, this object keeps a cache of looked up info;
    reusing an instance is significantly faster than using static methods."""
    def __init__(self):
        self.rev_cache = {}
        self.toc_cache = {}

    def fetch(self, citation, version, sectional):
        key = (tuple(citation), version, sectional)
        if key not in self.rev_cache:
            url = ''

            if sectional:
                view_name = 'section_reader_view'
                part = citation[0]
                section = citation[1]

                try:
                    url = reverse(view_name, args=(part, section, version))
                except NoReverseMatch:
                    # XXX We have some errors in our layers. Once those are
                    # fixed, we need to revisit this.
                    pass
            self.rev_cache[key] = url + '#' + '-'.join(to_markup_id(citation))
        return self.rev_cache[key]

    @staticmethod
    def of(citation, version, sectional):
        return SectionUrl().fetch(citation, version, sectional)
