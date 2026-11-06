"""Offline P0 backup/candidate/live safety tests. No GET, FTP, or publication."""
import importlib.util
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import prepare_live_analytics_patch as p0

spec = importlib.util.spec_from_file_location(
    "bundle", Path(__file__).resolve().parents[1] / "tools" / "check_p0_analytics_bundle.py")
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)


def fixtures():
    tail = b"</script>\n</body></html>\n"
    head = b"<html><body><h1>Example</h1>"
    original = head + b"x" * (p0.EXPECTED_ORIGINAL_SIZE - len(head) - len(tail)) + tail
    sibling_tail = p0.TAG + b"</body></html>\n"
    sibling_head = b"<html><body><h1>Sibling</h1>"
    sibling = sibling_head + b"x" * (p0.EXPECTED_SIBLING_SIZE - len(sibling_head) - len(sibling_tail)) + sibling_tail
    candidate = p0.build_one_line_patch(original, expected_sha256=p0.sha256(original))
    report = {"publication_status": "NOT_PUBLISHED", "source_url": p0.URL,
              "production_etag_at_read": p0.EXPECTED_ETAG,
              "original_sha256": p0.sha256(original), "prepared_sha256": p0.sha256(candidate),
              "production_original_bytes": len(original), "prepared_bytes": len(candidate),
              "change": p0.APPROVED_CHANGE,
              "mandatory_next_steps": list(p0.MANDATORY_NEXT_STEPS)}
    report["sibling_read_only_preflight"] = {
        "url": p0.SIBLING_URL, "etag": p0.EXPECTED_SIBLING_ETAG,
        "bytes": len(sibling), "sha256": p0.sha256(sibling),
        "analytics_tag_count": 1,
        "capture_stage": "PREFLIGHT_ONLY_NOT_UNDER_LOCK",
    }
    report["analytics_asset_read_only_preflight"] = {
        "url": p0.ASSET_URL, "status": 200, "mime": "application/javascript",
        "bytes": p0.EXPECTED_ASSET_SIZE, "sha256": p0.EXPECTED_ASSET_SHA256,
        "ga4_measurement_id_present": True,
        "capture_stage": "PREFLIGHT_ONLY_NOT_UNDER_LOCK",
        "ga4_event_receipt_verified": False,
    }
    live_sibling = {"sha256": p0.sha256(sibling), "etag": p0.EXPECTED_SIBLING_ETAG}
    return original, candidate, sibling, report, live_sibling


def valid_asset_evidence():
    # Metadata mirrors an independently verified GET. No live JS or network in tests.
    return {
        "status": 200, "url": p0.ASSET_URL, "mime": "application/javascript",
        "bytes": p0.EXPECTED_ASSET_SIZE, "sha256": p0.EXPECTED_ASSET_SHA256,
        "ga4_measurement_id_present": True,
    }


class BackupBundleTests(unittest.TestCase):
    def check(self, original, candidate, sibling, report, live_sibling, **kw):
        return bundle.check_bundle(
            original, candidate, sibling, report,
            kw.pop("live_html", original),
            kw.pop("live_etag", p0.EXPECTED_ETAG), live_sibling,
            kw.pop("live_asset", valid_asset_evidence()),
            expected_original_sha=kw.pop("expected_original_sha", p0.sha256(original)),
            expected_sibling_sha=kw.pop("expected_sibling_sha", p0.sha256(sibling)))

    def test_valid_bundle_reports_content_only_and_never_publication(self):
        original, candidate, sibling, report, live_sibling = fixtures()
        r = self.check(original, candidate, sibling, report, live_sibling)
        self.assertEqual(r["result"], "BACKUP_CANDIDATE_LIVE_BYTES_MATCH")
        self.assertFalse(r["publish_lock_verified_by_this_tool"])
        self.assertFalse(r["ga4_event_receipt_verified"])
        self.assertEqual(r["fresh_analytics_asset_sha256"], p0.EXPECTED_ASSET_SHA256)
        self.assertEqual(r["analytics_asset_recheck_scope"], "HTTP_CONTENT_ONLY_NOT_GA4_RECEIPT")
        self.assertFalse(r["published_by_this_tool"])

    def test_wrong_backup_same_size_rejected(self):
        original, candidate, sibling, report, live_sibling = fixtures()
        altered = original.replace(b"Example", b"ExAmple", 1)
        with self.assertRaisesRegex(p0.PreflightError, "original backup"):
            self.check(altered, candidate, sibling, report, live_sibling,
                       expected_original_sha=p0.sha256(original))

    def test_live_changed_after_backup_rejected(self):
        original, candidate, sibling, report, live_sibling = fixtures()
        changed = original.replace(b"Example", b"ExAmple", 1)
        with self.assertRaisesRegex(p0.PreflightError, "Live HTML"):
            self.check(original, candidate, sibling, report, live_sibling, live_html=changed)
        with self.assertRaisesRegex(p0.PreflightError, "Live HTML"):
            self.check(original, candidate, sibling, report, live_sibling, live_etag="new")

    def test_sibling_changed_after_backup_rejected(self):
        original, candidate, sibling, report, live_sibling = fixtures()
        live_sibling = dict(live_sibling, sha256="0" * 64)
        with self.assertRaisesRegex(p0.PreflightError, "Sibling changed"):
            self.check(original, candidate, sibling, report, live_sibling)

    def test_wrong_candidate_and_corrupt_preflight_report_rejected(self):
        original, candidate, sibling, report, live_sibling = fixtures()
        with self.assertRaisesRegex(p0.PreflightError, "Candidate"):
            self.check(original, candidate.replace(b"Example", b"ExAmple", 1),
                       sibling, report, live_sibling)
        with self.assertRaisesRegex(p0.PreflightError, "Preflight report"):
            self.check(original, candidate, sibling, dict(report, prepared_sha256="bad"), live_sibling)

    def test_missing_or_changed_fresh_analytics_asset_stops(self):
        original, candidate, sibling, report, live_sibling = fixtures()
        baseline = valid_asset_evidence()
        broken = [
            None,
            dict(baseline, status=301),
            dict(baseline, url="https://example.org/analytics.js"),
            dict(baseline, mime="text/html"),
            dict(baseline, bytes=p0.EXPECTED_ASSET_SIZE - 1),
            dict(baseline, sha256="0" * 64),  # Same size, changed JS bytes.
            dict(baseline, ga4_measurement_id_present=False),
        ]
        for evidence in broken:
            with self.subTest(evidence=evidence), self.assertRaisesRegex(
                    p0.PreflightError, "Analytics JS fresh live evidence"):
                self.check(original, candidate, sibling, report, live_sibling,
                           live_asset=evidence)

    def test_handoff_manifest_missing_or_rewritten_safety_steps_stops(self):
        # A structurally valid HTML candidate must not certify a handoff
        # whose lock, backups, event checks, or rollback steps were removed.
        original, candidate, sibling, report, live_sibling = fixtures()
        cases = [
            dict(report, mandatory_next_steps=[]),
            dict(report, mandatory_next_steps=list(p0.MANDATORY_NEXT_STEPS[:-1])),
            dict(report, change="replace entire article with generated HTML"),
        ]
        for bad in cases:
            with self.subTest(change=bad.get("change"), steps=bad.get("mandatory_next_steps")):
                with self.assertRaisesRegex(p0.PreflightError, "Preflight report"):
                    self.check(original, candidate, sibling, bad, live_sibling)

    def test_handoff_manifest_order_and_required_steps_are_exact(self):
        original, candidate, sibling, report, live_sibling = fixtures()
        # Reordering the operator instructions is not an approved handoff.
        tampered = dict(report, mandatory_next_steps=list(reversed(p0.MANDATORY_NEXT_STEPS)))
        with self.assertRaisesRegex(p0.PreflightError, "Preflight report"):
            self.check(original, candidate, sibling, tampered, live_sibling)
        self.assertEqual(self.check(original, candidate, sibling, report, live_sibling)
                         ["result"], "BACKUP_CANDIDATE_LIVE_BYTES_MATCH")

    def test_handoff_report_missing_preflight_evidence_stops(self):
        original, candidate, sibling, report, live_sibling = fixtures()
        for missing in ("sibling_read_only_preflight",
                        "analytics_asset_read_only_preflight"):
            with self.subTest(missing=missing), self.assertRaisesRegex(
                    p0.PreflightError, "Preflight (sibling|analytics asset) evidence"):
                bad = dict(report)
                bad.pop(missing)
                self.check(original, candidate, sibling, bad, live_sibling)

    def test_handoff_report_tampered_preflight_evidence_stops(self):
        original, candidate, sibling, report, live_sibling = fixtures()
        bad_cases = (
            ("sibling_read_only_preflight", "sha256", "0" * 64),
            ("sibling_read_only_preflight", "analytics_tag_count", 0),
            ("sibling_read_only_preflight", "capture_stage", "AFTER_UPLOAD"),
            ("analytics_asset_read_only_preflight", "sha256", "0" * 64),
            ("analytics_asset_read_only_preflight", "mime", "text/html"),
            ("analytics_asset_read_only_preflight", "ga4_event_receipt_verified", True),
        )
        for section, field, value in bad_cases:
            with self.subTest(section=section, field=field), self.assertRaisesRegex(
                    p0.PreflightError, "Preflight (sibling|analytics asset) evidence"):
                bad = dict(report)
                bad[section] = dict(report[section], **{field: value})
                self.check(original, candidate, sibling, bad, live_sibling)

    def test_sibling_backup_missing_tag_rejected(self):
        original, candidate, sibling, report, live_sibling = fixtures()
        altered = sibling.replace(p0.TAG, b"x" * len(p0.TAG), 1)
        with self.assertRaisesRegex(p0.PreflightError, "Sibling backup tracker"):
            self.check(original, candidate, altered, report, live_sibling,
                       expected_sibling_sha=p0.sha256(altered))

if __name__ == "__main__":
    unittest.main()
