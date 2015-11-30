from itertools import takewhile


def make_sortable(string):
    """Split a string into components, converting digits into ints so sorting
    works as we would expect"""
    if not string:      # base case
        return tuple()
    elif string[0].isdigit():
        prefix = "".join(takewhile(lambda c: c.isdigit(), string))
        return (int(prefix),) + make_sortable(string[len(prefix):])
    else:
        prefix = "".join(takewhile(lambda c: not c.isdigit(), string))
        return (prefix,) + make_sortable(string[len(prefix):])
