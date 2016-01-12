from itertools import takewhile

from cached_property import cached_property

from regulations.generator.layers.tree_builder import make_label_sortable


def sort_regtext_label(label):
    """ Make a regtext label sortable """
    sortable = [make_label_sortable(l)[0] for l in label]
    if len(sortable) > 4:
        sortable[4] = make_label_sortable(sortable[4], roman=True)[0]
    return sortable


class Label(object):
    """Rather than flip back and forth between list and string versions of
    node labels, wrap both here. Also provide properties for inspecting the
    label (e.g. to determine if it represents an interpretation, if another
    label is a child of this one"""
    def __init__(self, id=None, parts=None):
        if id is None:
            id = '-'.join(parts)
        if parts is None:
            parts = id.split('-')

        self._id = id
        self._parts = parts

    id = property(lambda self: self._id)
    parts = property(lambda self: self._parts)

    @cached_property
    def is_interp(self):
        return 'Interp' in self.parts

    @cached_property
    def is_interp_root(self):
        return self.parts and self.parts[-1] == 'Interp'

    @cached_property
    def prefix(self):
        """Interpretations have an added complication:
            1005-2-Interp-2 is a child of 1005-Interp"""
        return tuple(takewhile(lambda k: k != 'Interp', self.parts))

    @cached_property
    def sort_key(self):
        if not self.is_interp:
            return tuple(sort_regtext_label(self.parts))
        else:
            suffix = self.parts[len(self.prefix) + 1:]
            prefix_sortable = sort_regtext_label(self.prefix)
            suffix_sortable = [make_label_sortable(l)[0] for l in suffix]
            if len(suffix_sortable) > 1:
                suffix_sortable[1] = make_label_sortable(
                    suffix_sortable[1], roman=True)[0]
            return tuple(prefix_sortable + suffix_sortable)

    def __contains__(self, other):
        """Is the `other` label a child of this one?"""
        if isinstance(other, Label):
            prefix_match = other.prefix[:len(self.prefix)] == self.prefix
            lexical_match = other.parts[:len(self.parts)] == self.parts

            child_of_interp_root = (
                self.is_interp_root and other.is_interp and prefix_match)
            lexical_child = (
                lexical_match and other.is_interp == self.is_interp)
            return child_of_interp_root or lexical_child
        else:
            return False

    def __lt__(self, other):
        return self.sort_key < other.sort_key

    def __eq__(self, other):
        return isinstance(other, Label) and self.id == other.id
