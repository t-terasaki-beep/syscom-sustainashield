#!/usr/bin/env python3
"""Offline tests for the GitHub-only diagnosis alias link inventory."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from conversion_audit import audit  # noqa: E402
from summarize_diagnosis_links import summarize  # noqa: E402


class DiagnosisAliasSummaryTests(unittest.TestCase):
    def test_counts_per_target_and_source_with_no_canonical_decision(self):
        rows = [
            {"path": "index.html", "diagnosis_links": [
                {"target": "/shindan.html", "href": "shindan.html", "text": "旧"},
                {"target": "/shindan.html", "href": "/shindan.html?q=1", "text": "診断"},
                {"target": "/photo-diagnosis/", "href": "/photo-diagnosis/", "text": "新"},
            ]},
            {"path": "residential/index.html", "diagnosis_links": [
                {"target": "/photo-diagnosis/", "href": "../photo-diagnosis/", "text": "写真"},
            ]},
            {"path": "broken.html", "error": "invalid encoding"},
        ]
        report = summarize(rows)
        self.assertEqual(report["html_pages_audited"], 2)
        self.assertEqual(len(report["html_read_errors"]), 1)
        self.assertEqual(report["total_alias_link_occurrences"], 4)
        self.assertEqual(report["targets"]["/shindan.html"]["occurrences"], 2)
        self.assertEqual(report["targets"]["/shindan.html"]["referring_page_count"], 1)
        self.assertEqual(report["targets"]["/photo-diagnosis/"]["referring_page_count"], 2)
        self.assertFalse(report["live_http_redirect_or_canonical_verified"])
        self.assertFalse(report["external_backlinks_verified"])
        self.assertEqual(report["canonical_decision"], "pending_live_and_external_evidence")

    def test_real_html_parser_excludes_offsite_and_preserves_query(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "index.html").write_text(
                '<a href="/shindan.html?x=1">旧診断</a>'
                '<a href="https://elsewhere.example/shindan.html">外部</a>'
                '<a href="/photo-diagnosis/#step">写真診断</a>', encoding="utf-8")
            result = summarize(audit(root))
        self.assertEqual(result["total_alias_link_occurrences"], 2)
        self.assertEqual(result["targets"]["/shindan.html"]["links"][0]["href"],
                         "/shindan.html?x=1")

    def test_empty_inventory_is_not_taken_as_redirect_proof(self):
        result = summarize([{"path": "index.html", "diagnosis_links": []}])
        self.assertEqual(result["total_alias_link_occurrences"], 0)
        self.assertEqual(result["targets"]["/photo-diagnosis/"]["occurrences"], 0)
        self.assertEqual(result["canonical_decision"], "pending_live_and_external_evidence")


if __name__ == "__main__":
    unittest.main()
