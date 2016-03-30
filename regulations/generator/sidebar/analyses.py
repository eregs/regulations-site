from collections import namedtuple

import six

from regulations.generator.label import Label
from regulations.generator.node_types import label_to_text
from regulations.generator.sidebar.base import SidebarBase


class SxSEntry(namedtuple('SxSEntry', ['label', 'doc_number'])):
    def template_context(self):
        return {'doc_number': self.doc_number,
                'label_id': self.label.id,
                'text': label_to_text(self.label.parts, include_section=False,
                                      include_marker=True)}


class Analyses(SidebarBase):
    """Section-by-Section analyses information, which describes the reasons
    for _why_ a section/paragraph has been modified."""
    shorthand = 'analyses'

    def context(self, http_client, request):
        analyses = []
        data = self.fetch_data(http_client)
        if data:
            tree_labels = [Label(parts=t['label'])
                           for t in self.fetch_relevant_trees(http_client)]
            analyses.extend(
                sxs for sxs in data
                if any(sxs.label in label for label in tree_labels))
        analyses = [analysis.template_context()
                    for analysis in sorted(analyses)]
        return {
            'analyses': analyses,
            'human_label_id': label_to_text(
                self.label_parts, include_marker=True),
            'version': self.version
        }

    def fetch_data(self, http_client):
        """Retrieves SxSEntry data from the server"""
        if 'Interp' in self.label_id:
            reg_part = self.label_parts[0]
            doc_id = reg_part + '-Interp'
        else:
            doc_id = self.label_id
        data = http_client.layer('analyses', 'cfr', doc_id, self.version)

        if not data:
            return []

        return [
            SxSEntry(Label(label_id), doc_number=subdata[-1]['reference'][0])
            for label_id, subdata in six.iteritems(data)]
