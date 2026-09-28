import unittest

from src.manifest_loader import ManifestError, load_manifest


class LoadManifestTests(unittest.TestCase):
    def test_default_format_is_1(self):
        self.assertEqual(load_manifest("name: demo")["format"], 1)

    def test_format_2(self):
        self.assertEqual(load_manifest("name: demo\nformat: 2")["format"], 2)

    def test_format_3_is_accepted(self):
        self.assertEqual(load_manifest("name: demo\nformat: 3")["format"], 3)

    def test_unknown_format_is_rejected(self):
        with self.assertRaises(ManifestError):
            load_manifest("format: 9")

    def test_line_without_colon_is_rejected(self):
        with self.assertRaises(ManifestError):
            load_manifest("just words")
