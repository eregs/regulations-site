# vim: set encoding=utf-8
from itertools import takewhile
import re

# These node types represent categories of paragraphs/nodes within the
# regulation tree.
# APPENDIX - Auxiliary material at the end of the regulation
APPENDIX = u'appendix'
# INTERP - A special type of appendix dedicated to agency interpretations of
# the rest of the regulation
INTERP = u'interp'
# REGTEXT - The most common type of node. This represents paragraphs and
# sections
REGTEXT = u'regtext'
# SUBPART - Regulations are often split into lettered groupings of sections;
# the parent node of all of these sections is a SUBPART
SUBPART = u'subpart'
# SUBJGRP - Less common, but very similar to SUBPARTs, SUBJGRPs are groupings
# of sections without a specific letter designation
SUBJGRP = u'subjgrp'
# EMPTYPART - This is a "virtual" node type in the sense that it does not
# correspond to anything in the original regulation. Instead, it wraps
# sections which do not live inside a SUBPART/SUBJGRP to provide parallelism
EMPTYPART = u'emptypart'

PAREN_RE = re.compile(r'[()]')


def to_markup_id(id_parts):
    """Given the id parts from the JSON tree, convert to an id that can
    be used in the front end"""
    new_id = list(id_parts)
    if type_from_label(id_parts) in (APPENDIX, INTERP):
        return [PAREN_RE.sub('', part) for part in new_id]
    return new_id


def type_from_label(label):
    """Given a list of label parts, determine the associated node's type"""
    if 'Interp' in label:
        return INTERP
    if label[-1] == 'Subpart':
        return EMPTYPART
    if 'Subpart' in label:  # but not the final segment
        return SUBPART
    if 'Subjgrp' in label:
        return SUBJGRP
    if len(label) > 1 and label[1][:1].isalpha():
        return APPENDIX
    return REGTEXT


def label_to_text(label, include_section=True, include_marker=False):
    """Convert a label:list[string] into a human-readable string"""
    if len(label) == 1:
        return 'Regulation %s' % label[0]

    # Use short circuiting to grab the *first* type of label that matches
    return (_l2t_subterp(label) or _l2t_interp(label) or _l2t_appendix(label)
            or _l2t_section(label, include_section, include_marker))


MARKERLESS_REGEX = re.compile(r'^[hp]\d+')


def _not_markerless(l):
    return not MARKERLESS_REGEX.match(l)


def take_until_markerless(label_parts):
    return list(takewhile(_not_markerless, label_parts))


def _join_paragraph_tail(label_parts, join_with, prefix='', suffix=''):
    """Given the tail of paragraph markers in a label, convert them into a
    string, separated by the appropriate strings (join_with). Also remove any
    markers following a markerless paragraph"""
    label_parts = take_until_markerless(label_parts)
    if label_parts:
        return prefix + join_with.join(label_parts) + suffix
    else:
        return ""


def _l2t_subterp(label):
    """Helper function converting subterp labels to text. Assumes label has
    more then one segment"""
    if label[1:] == ['Subpart', 'Interp']:
        return 'Interpretations for Regulation Text of Part ' + label[0]
    elif label[1:] == ['Appendices', 'Interp']:
        return 'Interpretations for Appendices of Part ' + label[0]
    elif len(label) == 4 and label[1] == 'Subpart' and label[3] == 'Interp':
        interpretations_for = 'Interpretations for Subpart '
        return interpretations_for + label[2] + ' of Part ' + label[0]


def _l2t_interp(label):
    """Helper function converting interpretation labels to text. Assumes
    _l2t_subterp failed"""
    if 'Interp' in label:
        # Interpretation
        prefix = list(takewhile(lambda l: l != 'Interp', label))
        suffix = label[label.index('Interp') + 1:]
        if len(prefix) == 1 and suffix:
            # Interpretation introduction; for now we cop out
            return 'This Section'
        elif len(prefix) == 1:
            return 'Supplement I to Part %s' % prefix[0]
        elif suffix:
            suffix = _join_paragraph_tail(suffix, '.')
            return 'Supplement to %s-%s' % (label_to_text(prefix), suffix)
        else:
            return 'Supplement to %s' % label_to_text(prefix)


def _l2t_appendix(label):
    """Helper function converting appendix labels to text. Assumes
    _l2t_subterp and _l2t_interp failed"""
    if type_from_label(label) == APPENDIX:
        # Appendix
        label = take_until_markerless(label)
        if len(label) == 2:  # e.g. 225-B
            return 'Appendix ' + label[1] + ' to Part ' + label[0]
        elif len(label) == 3:  # e.g. 225-B-3
            return 'Appendix %s-%s' % tuple(label[1:])
        else:  # e.g. 225-B-3-a-4-i
            suffix = _join_paragraph_tail(label[3:], ')(', '(', ')')
            return 'Appendix %s-%s%s' % (label[1], label[2], suffix)


def _l2t_section(label, include_section, include_marker):
    """Helper function converting section labels to text. Assumes
    _l2t_subterp, _l2t_interp, and _l2t_appendix failed"""
    if include_marker:
        marker = u'§ '
    else:
        marker = ''

    if include_section:
        # Regulation Text with section number
        if len(label) == 2:  # e.g. 225-2
            return marker + '.'.join(label)
        else:  # e.g. 225-2-b-4-i-A
            suffix = _join_paragraph_tail(label[2:], ')(', '(', ')')
            return marker + '%s.%s%s' % (label[0], label[1], suffix)
    else:
        # Regulation Text without section number
        if len(label) == 2:  # e.g. 225-2
            return marker + label[1]
        else:  # e.g. 225-2-b-4-i-A
            suffix = _join_paragraph_tail(label[2:], ')(', '(', ')')
            return marker + label[1] + suffix
