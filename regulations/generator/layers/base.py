import abc
from collections import namedtuple

from regulations.generator.layers.location_replace import LocationReplace


class LayerBase(object):
    """Base class for most layers; each layer contains information which is
    added on top of the regulation, such as definitions, internal citations,
    keyterms, etc."""
    __metaclass__ = abc.ABCMeta

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

    @abc.abstractmethod
    def inline_replacements(self, text_index, original_text):
        """Return triplets of (original text, replacement text, offsets)"""
        raise NotImplementedError

    @abc.abstractmethod
    def attach_metadata(self, node):
        """Attach metadata to the provided node"""
        raise NotImplementedError


Replacement = namedtuple('Replacement',
                         ['original', 'replacement', 'locations'])


class InlineLayer(LayerBase):
    """Represents a layer which replaces text by looking at offsets"""

    @abc.abstractmethod
    def replacement_for(self, original, data):
        """Given the original text and the relevant data from a layer, create
        a (string) replacement, by, for example, running the data through a
        template"""
        raise NotImplementedError

    def apply_layer(self, text, label_id):
        """Entry point when processing the regulation tree. Given the node's
        text and its label_id, yield all replacement text"""
        data_with_offsets = ((entry, start, end)
                             for entry in self.layer.get(label_id, [])
                             for (start, end) in entry['offsets'])
        for data, start, end in data_with_offsets:
            start, end = int(start), int(end)
            original = text[start:end]
            replacement = self.replacement_for(original, data)
            yield (original, replacement, (start, end))

    def inline_replacements(self, text_index, original_text):
        """Apply multiple inline layers to given text (e.g. links,
        highlighting, etc.)"""
        layer_pairs = self.apply_layer(original_text, text_index)

        # convert from offset-based to a search and replace layer.
        for original, replacement, offset in layer_pairs:
            offset_locations = LocationReplace.find_all_offsets(
                original, original_text)
            locations = [offset_locations.index(offset)]
            yield Replacement(original, replacement, locations)

    def attach_metadata(self, node):
        """Noop"""
        pass


class SearchReplaceLayer(LayerBase):
    """Represents a layer which replaces text by searching for and replacing a
    specific substring. Also accounts for the string appearing multiple times
    (via the 'locations' field)"""
    _text_field = 'text'    # All but key terms follow this convention...

    @abc.abstractmethod
    def replacements_for(self, text, data):
        """Given the original text and the relevant data from a layer, create
        a (string) replacement, by, for example, running the data through a
        template. Returns a generator"""
        raise NotImplementedError

    def inline_replacements(self, text_index, original_text):
        """Entry point when processing the regulation tree. Given the node's
        label_id, attempt to find relevant layer data in self.layer"""
        for entry in self.layer.get(text_index, []):
            text = entry[self._text_field]
            for replacement in self.replacements_for(text, entry):
                yield Replacement(text, replacement, entry['locations'])

    def attach_metadata(self, node):
        """Noop"""
        pass


class ParagraphLayer(LayerBase):
    """Represents a layer which applies meta data to nodes"""

    def inline_replacements(self, text_index, original_text):
        """Noop"""
        return []
