from unittest import TestCase

from regulations.generator.layers.definitions import DefinitionsLayer


class DefinitionsLayerTest(TestCase):
    def test_replacement_for(self):
        layer = {
            '202-3': {'ref': 'account:202-2-a'},
            'referenced': {'account:202-2-a': {
                'reference': '202-2-a', 'term': 'account'}}
            }
        dl = DefinitionsLayer(layer)
        definition_link = dl.replacement_for('account', layer['202-3'])

        url = '<a href="#202-2-a" class="citation definition" '
        url += 'data-definition="202-2-a" data-defined-term="account">'
        url += 'account</a>'
        self.assertEquals(definition_link, url)
