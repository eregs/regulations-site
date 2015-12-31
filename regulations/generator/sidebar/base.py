import abc

from regulations.generator.subterp import filter_by_subterp


class SidebarBase(object):
    """Base class for Sidebar components. Provides an interface"""
    __metaclass__ = abc.ABCMeta

    def __init__(self, label_id, version):
        self.label_id = label_id
        self.label_parts = label_id.split('-')
        self.cfr_part = self.label_parts[0]
        self.version = version

    @abc.abstractproperty
    def shorthand(self):
        """Used for deriving templates, etc."""
        raise NotImplementedError

    @abc.abstractmethod
    def context(self, http_client, request):
        """Create a context dictionary specific to this sidebar type"""
        raise NotImplementedError

    def full_context(self, http_client, request):
        subcontext = self.context(http_client, request)
        subcontext.update(
            template_name='regulations/sidebar/{}.html'.format(self.shorthand)
        )
        return subcontext

    def fetch_relevant_trees(self, http_client):
        """If using subterps, we might be getting a list of relevant trees
        rather than a single node."""
        is_interp = 'Interp' in self.label_parts
        is_complex = set(['Subpart', 'Appendices']) & set(self.label_parts)
        is_subterp = is_interp and is_complex
        if is_subterp:
            interp = http_client.regulation(
                self.cfr_part + '-Interp', self.version)
            if interp:
                for tree_node in filter_by_subterp(
                        interp['children'], self.label_parts, self.version):
                    yield tree_node
        else:
            node = http_client.regulation(self.label_id, self.version)
            if node:
                yield node
