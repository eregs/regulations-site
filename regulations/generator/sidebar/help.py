from regulations.generator.sidebar.base import SidebarBase


class Help(SidebarBase):
    shorthand = 'help'

    def context(self, http_client):
        return {}
