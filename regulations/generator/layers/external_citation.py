import urllib
from django.template import loader
import utils

from regulations.generator.layers.base import InlineLayer


class ExternalCitationLayer(InlineLayer):
    shorthand = 'external'
    data_source = 'terms'

    def __init__(self, layer):
        self.layer = layer

    @staticmethod
    def generate_fdsys_href_tag(text, parameters):
        """ Generate an href tag to FDSYS. """
        parameters['year'] = "mostrecent"

        if 'link-type' not in parameters:
            parameters['link-type'] = "html"

        fdsys_url_base = "http://api.fdsys.gov/link"
        fdsys_url = "%s?%s" % (fdsys_url_base, urllib.urlencode(parameters))

        template = loader.get_template(
            'regulations/layers/external_citation.html')
        context = {
            'citation': {
                'url': fdsys_url,
                'label': text}}
        return utils.render_template(template, context)

    @staticmethod
    def generate_cfr_link(text, citation):
        """ Convert the CFR references into an HTML <a href> tag. """
        parameters = {'titlenum': citation[0], 'partnum': citation[1]}
        if len(citation) > 2:
            parameters['sectionnum'] = citation[2]

        parameters['link-type'] = 'xml'
        parameters['collection'] = 'cfr'
        return ExternalCitationLayer.generate_fdsys_href_tag(text, parameters)

    @staticmethod
    def generate_public_law_link(text, citation):
        """ Convert the Public Law references into an HTML <a href> tag. """
        parameters = {
            'congress': citation[0],
            'lawnum': citation[1],
            'collection': 'plaw',
            'lawtype': 'public'}
        return ExternalCitationLayer.generate_fdsys_href_tag(text, parameters)

    @staticmethod
    def generate_statutes_at_large_link(text, citation):
        parameters = {
            'statutecitation': '%s stat %s' % (citation[0], citation[2]),
            'collection': 'plaw'}
        return ExternalCitationLayer.generate_fdsys_href_tag(text, parameters)

    @staticmethod
    def generate_uscode_link(text, citation):
        """ Convert the US Code references into an HTML <a href> tag. """
        parameters = {
            "collection": "uscode",
            "title": citation[0],
            "section": citation[1]}
        return ExternalCitationLayer.generate_fdsys_href_tag(text, parameters)

    def citation_type_to_generator(self, citation_type):
        generator_map = {
            'USC': ExternalCitationLayer.generate_uscode_link,
            'CFR': ExternalCitationLayer.generate_cfr_link,
            'PUBLIC_LAW': self.generate_public_law_link,
            'STATUTES_AT_LARGE': self.generate_statutes_at_large_link
        }
        generator = generator_map[citation_type]
        return generator

    def replacement_for(self, original, data):
        """Given link text and relevant data, create an appropriate link"""
        generator = self.citation_type_to_generator(data['citation_type'])
        return generator(original, data['citation'])
