from datetime import datetime
import re

import six
from django.template import Context


def convert_to_python(data):
    """Convert raw data (e.g. from json conversion) into the appropriate
    Python objects"""
    if isinstance(data, six.string_types):
        #   Dates
        if re.match(r'^\d{4}-\d{2}-\d{2}$', data):
            return datetime.strptime(data, '%Y-%m-%d')
    if isinstance(data, dict):
        new_data = {}
        for key in data:
            new_data[key] = convert_to_python(data[key])
        return new_data
    if isinstance(data, tuple):
        return tuple(map(convert_to_python, data))
    if isinstance(data, list):
        return list(map(convert_to_python, data))

    return data


def render_template(template, context):
    c = Context(context)
    return template.render(c).strip('\n')


def is_contained_in(child, parent):
    '''
        Return True if child is a child node of the parent.

        Node labels are hierarchical paths, with segments separated
        by '-'. As an edge case, a node label is also a child of itself.
    '''
    child_segments = child.split('-')
    parent_segments = parent.split('-')
    return child_segments[:len(parent_segments)] == parent_segments
