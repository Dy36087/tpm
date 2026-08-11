from importlib import import_module

from django.test import SimpleTestCase


class ViewsImportTests(SimpleTestCase):
    def test_views_import_without_optional_export_dependencies(self):
        module = import_module("cadferramentas.views")
        self.assertTrue(hasattr(module, "cadferramentas"))
