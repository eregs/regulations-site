from regulations.generator.sidebar.base import SidebarBase


class DiffHelp(SidebarBase):
    """Help info specific to Diffs"""
    shorthand = 'diff_help'

    def context(self, http_client, request):
        return {}
