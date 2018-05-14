# -*- coding: utf-8 -*-
from regulations.generator import title_parsing
from regulations.generator.layers.base import ParagraphLayer
from regulations.generator.section_url import SectionUrl
from regulations.generator.toc import (
    toc_interp, toc_sect_appendix, toc_subpart)


class TableOfContentsLayer(ParagraphLayer):
    shorthand = 'toc'
    data_source = 'toc'

    def __init__(self, layer):
        self.layer = layer
        self.sectional = False
        self.version = None
        self.section_url = SectionUrl()

    def attach_metadata(self, node):
        text_index = node['label_id']
        if text_index in self.layer:
            layer_elements = self.layer[text_index]

            toc_list = []
            for data in layer_elements:
                if 'Subpart' in data['index']:
                    toc_list.append(toc_subpart(data, toc_list, self.layer))
                elif 'Interp' in data['index']:
                    toc_list.append(toc_interp(data, toc_list, self.layer))
                else:
                    toc_list.append(toc_sect_appendix(data, toc_list))

            for el in toc_list:
                el['url'] = self.section_url.fetch(
                    el['index'], self.version, self.sectional)
                for sub in el.get('sub_toc', []):
                    sub['url'] = self.section_url.fetch(
                        sub['index'], self.version, self.sectional)
            node['TOC'] = toc_list

    @staticmethod
    def section(element, data):
        title_data = title_parsing.section(data)
        if title_data:
            element.update(title_data)

    @staticmethod
    def appendix_supplement(element, data, seen_appendix=False):
        as_data = title_parsing.appendix_supplement(data)
        if as_data:
            element.update(as_data)
        if element.get('is_appendix'):
            element['is_first_appendix'] = not seen_appendix
