from collections import defaultdict
import os

from django.apps import AppConfig
from django.template.loaders.app_directories import get_app_template_dirs


class RegulationsConfig(AppConfig):
    name = 'regulations'
    # Maps node label_id's to the template which should be used to render
    # them. Warning: global state
    custom_tpls = {}
    node_type_tpls = defaultdict(lambda: "regulations/tree/default.html")

    def ready(self):
        """Called (almost) once per application startup. Should only contain
        idempotent operations"""
        self.precompute_custom_templates()
        self.precompute_node_type_templates()

    @staticmethod
    def _find_templates(location, add_to):
        """Helper method for shared search-templates-add-to-dict
        functionality"""
        search_path = os.path.join('templates', 'regulations', location)
        file_names = {file_name
                      for template_dir in get_app_template_dirs(search_path)
                      for file_name in os.listdir(template_dir)
                      if os.path.isfile(os.path.join(template_dir, file_name))}
        for file_name in file_names:
            ident, _ = os.path.splitext(file_name)
            add_to[ident] = 'regulations/{}/{}'.format(location, file_name)

    @classmethod
    def precompute_custom_templates(cls):
        """We allow agencies to provide templates for specific nodes in the
        regulation tree. Rather than have the rendering code inspect which
        templates are available at render time, we'll find the special cases
        during the application startup"""
        cls._find_templates('custom_nodes', cls.custom_tpls)

    @classmethod
    def precompute_node_type_templates(cls):
        """Different node types may display differently. Scan the provided
        templates to see if any node-type-specific templates are present."""
        cls._find_templates('tree', cls.node_type_tpls)
