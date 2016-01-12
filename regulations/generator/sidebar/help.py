from regulations.generator.sidebar.base import SidebarBase


class Help(SidebarBase):
    """Help info; composed of a template only"""
    shorthand = 'help'

    def context(self, http_client):
        return {}
