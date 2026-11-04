"""Offline tests: no site/network calls or production changes."""
import tempfile
from pathlib import Path
import unittest
from audit_photo_diagnosis_repo_links import audit, target_for_href, source_url_path


class TestPhotoDiagnosisRepoLinks(unittest.TestCase):
    def test_legacy_relative_from_root(self):
        self.assertEqual(target_for_href('/', 'shindan.html'), '/shindan.html')

    def test_new_absolute_with_query(self):
        self.assertEqual(target_for_href('/', 'https://syscom-sustaina-shield.com/photo-diagnosis/?utm=abc'), '/photo-diagnosis/')

    def test_external_host_is_ignored(self):
        self.assertIsNone(target_for_href('/', 'https://other.example/shindan.html'))
        self.assertIsNone(target_for_href('/', 'https://syscom-sustaina-shield.com.evil.tld/shindan.html'))

    def test_unrelated_path_is_ignored(self):
        self.assertIsNone(target_for_href('/', '/photo-diagnosis/other/'))

    def test_source_url_mapping(self):
        root = Path('/some/path')
        self.assertEqual(source_url_path(root, root/'index.html'), '/')
        self.assertEqual(source_url_path(root, root/'contact.html'), '/contact.html')
        self.assertEqual(source_url_path(root, root/'residential'/'index.html'), '/residential/')

    def test_audit_counts_only_html_anchor_links(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root/'index.html').write_text('<a href="shindan.html">one</a><a href="/photo-diagnosis/">two</a><script>"shindan.html"</script>', encoding='utf-8')
            (root/'contact.html').write_text('<A href="/shindan.html#form">three</A>', encoding='utf-8')
            (root/'node_modules').mkdir()
            (root/'node_modules'/'junk.html').write_text('<a href="/shindan.html">ignored</a>', encoding='utf-8')
            out = audit(root)
            self.assertEqual(out['html_files_scanned'], 2)
            self.assertEqual(out['counts'], {'/shindan.html': 2, '/photo-diagnosis/': 1})
            self.assertEqual(len(out['sources']), 2)
            self.assertEqual(out['redirect_or_canonical_changes'], 0)


if __name__ == '__main__':
    unittest.main()
