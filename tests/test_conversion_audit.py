#!/usr/bin/env python3
"""Offline regression tests for static-only conversion auditing."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from conversion_audit import Page, audit  # noqa: E402


class PlaceholderFormTests(unittest.TestCase):
    def parse(self, html):
        page = Page()
        page.feed(html)
        return page

    def test_existing_contact_html_is_flagged(self):
        source = (ROOT / "contact.html").read_text(encoding="utf-8")
        page = self.parse(source)
        self.assertEqual(page.forms, 1)
        self.assertEqual(page.placeholder_forms, 1)

    def test_real_action_form_not_flagged(self):
        page = self.parse('<form method="post" action="/api/contact"><input name="email"></form>')
        self.assertEqual(page.forms, 1)
        self.assertEqual(page.placeholder_forms, 0)

    def test_ajax_return_false_alone_does_not_imply_broken(self):
        page = self.parse('<form onsubmit="sendAsync(); return false;"><button>送信</button></form>')
        self.assertEqual(page.placeholder_forms, 0)

    def test_explicit_english_stub_flagged(self):
        page = self.parse('<form onsubmit="alert(\'Not implemented\'); return false;"></form>')
        self.assertEqual(page.placeholder_forms, 1)

    def test_warning_in_audit_json(self):
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            (root / "stub.html").write_text(
                '<html><head><title>Test</title><meta name="description" content="x"></head>'
                '<body><h1>Test</h1><form onsubmit="alert(\'送信先を実装してください\'); return false;">'
                '<button type="submit">送信</button></form></body></html>', encoding="utf-8"
            )
            result = audit(root)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["forms"], 1)
        self.assertEqual(result[0]["placeholder_forms"], 1)
        self.assertIn("placeholder_form_submit", result[0]["warnings"])


if __name__ == "__main__":
    unittest.main()
