from datetime import datetime
import re

import six


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


def roman_nums():
    """Generator for roman numerals."""
    mapping = [
        (1, 'i'), (4, 'iv'), (5, 'v'), (9, 'ix'),
        (10, 'x'), (40, 'xl'), (50, 'l'), (90, 'xc'),
        (100, 'c'), (400, 'cd'), (500, 'd'), (900, 'cm'),
        (1000, 'm')
        ]
    i = 1
    while True:
        next_str = ''
        remaining_int = i
        remaining_mapping = list(mapping)
        while remaining_mapping:
            (amount, chars) = remaining_mapping.pop()
            while remaining_int >= amount:
                next_str += chars
                remaining_int -= amount
        yield next_str
        i += 1
