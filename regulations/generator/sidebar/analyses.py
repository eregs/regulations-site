from regulations.generator.layers.analyses import SectionBySectionLayer
from regulations.generator.node_types import label_to_text
from regulations.generator.sidebar.base import SidebarBase


class Analyses(SidebarBase):
    shorthand = 'analyses'

    def context(self, http_client):
        data = self.fetch_layer_data(http_client)
        analyses = []
        if data:
            layer = SectionBySectionLayer(data)
            for tree in self.fetch_relevant_trees(http_client):
                result = layer.apply_layer('-'.join(tree['label']))
                if result:
                    analyses.extend(result[1])
        return {
            'analyses': analyses,
            'human_label_id': label_to_text(
                self.label_parts, include_marker=True),
            'version': self.version
        }

    def fetch_layer_data(self, http_client):
        if 'Interp' in self.label_id:
            reg_part = self.label_parts[0]
            return http_client.layer(
                'analyses', reg_part + '-Interp', self.version)
        else:
            return http_client.layer('analyses', self.label_id, self.version)
