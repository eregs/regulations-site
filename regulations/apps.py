from collections import defaultdict
import os

from django.apps import AppConfig
from django.template.loaders.app_directories import get_app_template_dirs


class RegulationsConfig(AppConfig):
    name = 'regulations'
    # Maps node label_id's to the template which should be used to render
    # them. Warning: global state
    precomputed_templates = defaultdict(
        lambda: "regulations/tree-with-wrapper.html")

    def ready(self):
        """Called (almost) once per application startup. Should only contain
        idempotent operations"""
        self.precompute_custom_templates()

    @staticmethod
    def precompute_custom_templates():
        """We allow agencies to provide templates for specific nodes in the
        regulation tree. Rather than have the rendering code inspect which
        templates are available at render time, we'll find the special cases
        during the application startup"""
        search_path = os.path.join('templates', 'regulations', 'custom_nodes')
        file_names = {file_name
                      for template_dir in get_app_template_dirs(search_path)
                      for file_name in os.listdir(template_dir)
                      if os.path.isfile(os.path.join(template_dir, file_name))}
        for file_name in file_names:
            ident, _ = os.path.splitext(file_name)
            RegulationsConfig.precomputed_templates[ident] = (
                'regulations/custom_nodes/' + file_name)
