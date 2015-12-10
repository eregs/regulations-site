import abc


class LayerBase(object):
    """Base class for most layers; each layer contains information which is
    added on top of the regulation, such as definitions, internal citations,
    keyterms, etc."""
    __metaclass__ = abc.ABCMeta

    # @see layer_type
    INLINE = 'inline'
    PARAGRAPH = 'paragraph'
    SEARCH_REPLACE = 'search_replace'

    @abc.abstractproperty
    def shorthand(self):
        """A short description for this layer. This is used in query strings
        and the like to define which layers should be used"""
        raise NotImplementedError

    @abc.abstractproperty
    def data_source(self):
        """Data is pulled from the API; this field indicates the name of the
        endpoint to pull data from"""
        raise NotImplementedError

    @abc.abstractproperty
    def layer_type(self):
        """Layer data can be applied in a few ways, attaching itself to a
        node, replacing text based on offset, or replacing text based on
        searching. Which type is this layer?"""
        raise NotImplementedError
