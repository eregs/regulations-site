from regulations.generator.sidebar.base import SidebarBase
from regulations.views.utils import regulation_meta


class PrintPart(SidebarBase):
    shorthand = 'print_part'

    def context(self, http_client, request):
        meta = regulation_meta(self.cfr_part, self.version)

        return {
            'cfr_title': meta.get('cfr_title_number'),
            'cfr_part': self.cfr_part,
            'version': self.version,
        }
