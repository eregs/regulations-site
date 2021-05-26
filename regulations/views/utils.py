import logging

from regulations.views.errors import NotInSubpart


logger = logging.getLogger(__name__)


def find_subpart(section, node, subpart=None):
    value = None
    if node['type'] == 'section' and node['identifier'][1] == section:
        if subpart is None:
            raise NotInSubpart()
        return subpart
    elif node['type'] == 'subpart' and node['children'] is not None:
        for child in node['children']:
            value = find_subpart(section, child, node['identifier'][0])
            if value is not None:
                break
    elif node['children'] is not None:
        for child in node['children']:
            value = find_subpart(section, child, subpart)
            if value is not None:
                break
    return value
