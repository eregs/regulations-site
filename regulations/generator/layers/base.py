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


class InlineLayer(LayerBase):
    """Represents a layer which replaces text by looking at offsets"""
    layer_type = LayerBase.INLINE

    @abc.abstractmethod
    def replacement_for(self, original, data):
        """Given the original text and the relevant data from a layer, create
        a (string) replacement, by, for example, running the data through a
        template"""
        raise NotImplementedError

    def apply_layer(self, text, text_index):
        """Entry point when processing the regulation tree. Given the node's
        text and its index, yield all replacement text"""
        data_with_offsets = ((entry, start, end)
                             for entry in self.layer.get(text_index, [])
                             for (start, end) in entry['offsets'])
        for data, start, end in data_with_offsets:
            start, end = int(start), int(end)
            original = text[start:end]
            replacement = self.replacement_for(original, data)
            yield (original, replacement, (start, end))
