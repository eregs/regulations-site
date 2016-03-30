import string
from django.template import loader

from regulations.generator.layers import utils
from regulations.generator.layers.base import SearchReplaceLayer


class KeyTermsLayer(SearchReplaceLayer):
    shorthand = 'keyterms'
    data_source = 'keyterms'
    _text_field = 'key_term'

    def __init__(self, layer):
        self.layer = layer
        self.template = loader.get_template('regulations/layers/key_term.html')

    def remove_punctuation(self, punctuated):
        translate_table = dict((ord(c), None) for c in string.punctuation)
        return punctuated.translate(translate_table)

    def replacements_for(self, original, data):
        key_term = {'key_term': original,
                    'phrase': self.remove_punctuation(original)}
        context = {'key_term': key_term}
        yield utils.render_template(self.template, context)
