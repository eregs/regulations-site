import abc


class SidebarBase(object):
    """Base class for Sidebar components. Provides an interface"""
    __metaclass__ = abc.ABCMeta

    def __init__(self, label_parts, version):
        self.label_parts = label_parts
        self.label_id = "-".join(label_parts)
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
        node = http_client.regulation(self.label_id, self.version)
        if node:
            yield node
