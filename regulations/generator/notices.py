def filter_labeled_children(sxs):
    """ Some children don't have labels. We display those with their parents.
    The other children are displayed when they are independently, specifically
    requested. """
    return [s for s in sxs['children'] if 'label' not in s]


def non_empty_sxs(sxs):
    has_paragraphs = len(sxs['paragraphs']) > 0
    has_unlabeled_children = len(filter_labeled_children(sxs)) > 0
    return (has_paragraphs or has_unlabeled_children)


def add_depths(sxs, starting_depth):
    """ We use depth numbers in header tags  to determine how titles are
    output. """

    sxs['depth'] = starting_depth
    for s in sxs['children']:
        add_depths(s, starting_depth+1)


def find_label_in_sxs(sxs_list, label_id, fr_page=None):
    """ Given a tree of SXS sections, find a non-empty sxs that matches
    label_id. Some notices may have the same label appearing multiple times;
    use fr_page to distinguish, defaulting to the first"""

    matches = []

    for s in sxs_list:
        if label_id in s.get('labels', [s.get('label')]) and non_empty_sxs(s):
            matches.append(s)
        elif s['children']:
            sxs = find_label_in_sxs(s['children'], label_id, fr_page)
            if sxs and non_empty_sxs(sxs):
                matches.append(sxs)

    perfect_match = [m for m in matches if m.get('page') == fr_page]
    if perfect_match:
        return perfect_match[0]
    if matches:
        return matches[0]
