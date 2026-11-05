"""Offline tests. No network, credentials, FTP, or publication."""
import importlib.util
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

MOD_PATH = Path(__file__).resolve().parents[1] / "tools" / "prepare_live_analytics_patch.py"
spec = importlib.util.spec_from_file_location("preflight", MOD_PATH)
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)


def sample() -> bytes:
    tail = b"</script>\n</body></html>\n"
    head = b"<html><body><main><h1>Example</h1>"
    return head + b"x" * (preflight.EXPECTED_ORIGINAL_SIZE - len(head) - len(tail)) + tail


def sibling_fixture() -> bytes:
    head = b"<html><body><h1>Sibling</h1>"
    tail = preflight.TAG + b"</body></html>\n"
    return head + b"x" * (preflight.EXPECTED_SIBLING_SIZE - len(head) - len(tail)) + tail


class SiblingSnapshotTests(unittest.TestCase):
    def test_baseline_sibling_produces_preflight_only_sha_evidence(self):
        raw = sibling_fixture()
        with patch.object(preflight, "EXPECTED_SIBLING_SHA256", preflight.sha256(raw)):
            record = preflight.validate_sibling_snapshot(raw, preflight.EXPECTED_SIBLING_ETAG)
        self.assertEqual(record["sha256"], preflight.sha256(raw))
        self.assertEqual(record["analytics_tag_count"], 1)
        self.assertEqual(record["capture_stage"], "PREFLIGHT_ONLY_NOT_UNDER_LOCK")

    def test_sibling_etag_or_size_drift_stops(self):
        raw = sibling_fixture()
        with self.assertRaisesRegex(preflight.PreflightError, "ETag changed"):
            preflight.validate_sibling_snapshot(raw, "changed")
        with self.assertRaisesRegex(preflight.PreflightError, "size changed"):
            preflight.validate_sibling_snapshot(raw + b"x", preflight.EXPECTED_SIBLING_ETAG)

    def test_sibling_same_size_content_drift_stops(self):
        raw = sibling_fixture()
        altered = raw.replace(b"<h1>Sibling", b"<h1>SiBling", 1)
        self.assertEqual(len(raw), len(altered))
        with patch.object(preflight, "EXPECTED_SIBLING_SHA256", preflight.sha256(raw)):
            with self.assertRaisesRegex(preflight.PreflightError, "SHA-256 changed"):
                preflight.validate_sibling_snapshot(altered, preflight.EXPECTED_SIBLING_ETAG)

    def test_sibling_duplicate_tracking_ref_stops_even_with_matching_digest(self):
        raw = sibling_fixture()
        modified = raw.replace(b"x" * len(preflight.TAG), preflight.TAG, 1)
        self.assertEqual(len(raw), len(modified))
        with patch.object(preflight, "EXPECTED_SIBLING_SHA256", preflight.sha256(modified)):
            with self.assertRaisesRegex(preflight.PreflightError, "tag count"):
                preflight.validate_sibling_snapshot(modified, preflight.EXPECTED_SIBLING_ETAG)

    def test_sibling_footer_incomplete_stops_even_with_matching_digest(self):
        raw = sibling_fixture()
        modified = raw[:-7] + b"x" * 7
        self.assertEqual(len(raw), len(modified))
        with patch.object(preflight, "EXPECTED_SIBLING_SHA256", preflight.sha256(modified)):
            with self.assertRaisesRegex(preflight.PreflightError, "footer incomplete"):
                preflight.validate_sibling_snapshot(modified, preflight.EXPECTED_SIBLING_ETAG)


def analytics_asset_fixture() -> bytes:
    # Offline test bytes only: no real production script is stored in tests.
    start = b"// " + preflight.GA4_MEASUREMENT_ID + b"\\n"
    return start + b"x" * (preflight.EXPECTED_ASSET_SIZE - len(start))


class AnalyticsAssetPreflightTests(unittest.TestCase):
    def test_pinned_js_passes_with_normal_javascript_mime(self):
        raw = analytics_asset_fixture()
        with patch.object(preflight, "EXPECTED_ASSET_SHA256", preflight.sha256(raw)):
            proof = preflight.validate_analytics_asset(
                raw, content_type="text/javascript; charset=utf-8"
            )
        self.assertEqual(proof["bytes"], 8607)
        self.assertTrue(proof["ga4_measurement_id_present"])
        self.assertFalse(proof["ga4_event_receipt_verified"])
        self.assertEqual(proof["capture_stage"], "PREFLIGHT_ONLY_NOT_UNDER_LOCK")

    def test_changed_asset_sha_stops_even_with_same_size_and_ga4_id(self):
        raw = analytics_asset_fixture()
        tampered = raw[:-1] + b"q"
        self.assertEqual(len(raw), len(tampered))
        with patch.object(preflight, "EXPECTED_ASSET_SHA256", preflight.sha256(raw)):
            with self.assertRaisesRegex(preflight.PreflightError, "SHA-256"):
                preflight.validate_analytics_asset(
                    tampered, content_type="application/javascript"
                )

    def test_non_javascript_or_missing_mime_stops(self):
        raw = analytics_asset_fixture()
        with patch.object(preflight, "EXPECTED_ASSET_SHA256", preflight.sha256(raw)):
            for mime in ("text/html", "text/plain", None):
                with self.subTest(mime=mime), self.assertRaisesRegex(
                    preflight.PreflightError, "Content-Type"
                ):
                    preflight.validate_analytics_asset(raw, content_type=mime)

    def test_redirect_or_non_200_status_stops(self):
        raw = analytics_asset_fixture()
        with patch.object(preflight, "EXPECTED_ASSET_SHA256", preflight.sha256(raw)):
            for status, url in ((301, preflight.ASSET_URL),
                                (200, "https://example.org/fallback.js")):
                with self.subTest(status=status, url=url), self.assertRaisesRegex(
                    preflight.PreflightError, "HTTP status or final URL"
                ):
                    preflight.validate_analytics_asset(
                        raw, content_type="text/javascript",
                        status=status, actual_url=url
                    )

    def test_length_and_ga4_id_missing_stop(self):
        raw = analytics_asset_fixture()
        with patch.object(preflight, "EXPECTED_ASSET_SHA256", preflight.sha256(raw)):
            with self.assertRaisesRegex(preflight.PreflightError, "byte size"):
                preflight.validate_analytics_asset(
                    raw[:-1], content_type="text/javascript"
                )
        missing = raw.replace(preflight.GA4_MEASUREMENT_ID,
                              b"x" * len(preflight.GA4_MEASUREMENT_ID), 1)
        with patch.object(preflight, "EXPECTED_ASSET_SHA256", preflight.sha256(missing)):
            with self.assertRaisesRegex(preflight.PreflightError, "measurement ID missing"):
                preflight.validate_analytics_asset(
                    missing, content_type="text/javascript"
                )



class PatchTests(unittest.TestCase):
    def test_insertion_is_exactly_one_tag(self):
        raw = sample()
        edited = preflight.build_one_line_patch(raw, expected_sha256=preflight.sha256(raw))
        self.assertEqual(len(edited), 25239)
        self.assertEqual(edited.replace(preflight.TAG, b""), raw)
        self.assertEqual(edited.count(preflight.TAG), 1)
        self.assertTrue(edited.endswith(preflight.TAG + b"</body></html>\n"))
        self.assertEqual(edited[:-len(b"</body></html>\n")].count(b"</script>\n"), 1)

    def test_independent_patched_sha_pin_rejects_mismatch(self):
        # A correctly sized, exactly one-tag candidate must also match the
        # independently recorded publication SHA, not just the source digest.
        raw = sample()
        original_sha = preflight.sha256(raw)
        with patch.object(preflight, "EXPECTED_ORIGINAL_SHA256", original_sha), \
             patch.object(preflight, "EXPECTED_PATCHED_SHA256", "0" * 64):
            with self.assertRaisesRegex(preflight.PreflightError, "Patched SHA-256"):
                preflight.build_one_line_patch(raw, expected_sha256=original_sha)

    def test_independent_patched_sha_pin_accepts_exact_candidate(self):
        raw = sample()
        original_sha = preflight.sha256(raw)
        candidate = raw.replace(b"</body>", preflight.TAG + b"</body>", 1)
        with patch.object(preflight, "EXPECTED_ORIGINAL_SHA256", original_sha), \
             patch.object(preflight, "EXPECTED_PATCHED_SHA256", preflight.sha256(candidate)):
            actual = preflight.build_one_line_patch(raw, expected_sha256=original_sha)
        self.assertEqual(actual, candidate)
        self.assertEqual(len(actual), preflight.EXPECTED_PATCHED_SIZE)

    def test_same_size_and_shape_but_wrong_sha_fails_closed(self):
        # An old or altered production page could be exactly the same length.
        # The standalone builder must refuse it even without fetch_live().
        raw = sample()
        self.assertEqual(len(raw), preflight.EXPECTED_ORIGINAL_SIZE)
        self.assertIn(b"<h1>", raw)
        with self.assertRaisesRegex(preflight.PreflightError, "Original SHA-256"):
            preflight.build_one_line_patch(raw)

    def test_duplicate_refuses_to_modify(self):
        ref = b"ss-analytics.js"
        raw = sample().replace(b"x" * len(ref), ref, 1)
        self.assertEqual(len(raw), preflight.EXPECTED_ORIGINAL_SIZE)
        with self.assertRaises(preflight.PreflightError):
            preflight.build_one_line_patch(raw)

    def test_alternate_tracking_blocks_insertion(self):
        # A page already sending page_view through gtag or GTM must be reviewed,
        # not silently equipped with a second analytics loader.
        for marker in (
            b"googletagmanager.com/gtag/js",
            b"googletagmanager.com/gtm.js",
            b"gtag('config'",
            b'gtag("config"',
            b"G-ELZG7B45NH",
        ):
            with self.subTest(marker=marker):
                raw = sample().replace(b"x" * len(marker), marker, 1)
                self.assertEqual(len(raw), preflight.EXPECTED_ORIGINAL_SIZE)
                with self.assertRaisesRegex(preflight.PreflightError, "Other GA4/GTM"):
                    preflight.build_one_line_patch(raw)

    def test_missing_h1_fails_closed(self):
        raw = sample().replace(b"<h1>Example</h1>", b"<p>Example</p>" + b"x" * 2)
        self.assertEqual(len(raw), preflight.EXPECTED_ORIGINAL_SIZE)
        with self.assertRaises(preflight.PreflightError):
            preflight.build_one_line_patch(raw)

    def test_size_drift_fails_closed(self):
        with self.assertRaises(preflight.PreflightError):
            preflight.build_one_line_patch(sample() + b"x")

    def test_unexpected_footer_fails_closed(self):
        raw = sample().replace(b"</script>\n</body></html>\n", b"</script>\n</boDY></html>\n")
        with self.assertRaises(preflight.PreflightError):
            preflight.build_one_line_patch(raw)

    def test_etag_weak_missing_or_malformed_is_rejected(self):
        for value in (
            None, "", 'W/"6262-65f3790c0687e"',
            "6262-65f3790c0687e",  # Bare token used to slip past the ETag gate.
            '"6262-65f3790c0687e"trailing',
            ' "6262-65f3790c0687e"noise ',
            '""',
        ):
            with self.subTest(value=value), self.assertRaises(preflight.PreflightError):
                preflight.normalize_etag(value)
        self.assertEqual(preflight.normalize_etag('"6262-65f3790c0687e"'),
                         preflight.EXPECTED_ETAG)
        # Whitespace around an otherwise valid quoted validator is harmless.
        self.assertEqual(preflight.normalize_etag('  "6262-65f3790c0687e"  '),
                         preflight.EXPECTED_ETAG)



class LocalPreflightOutputTests(unittest.TestCase):
    """No network and no real production HTML is ever written here."""

    def test_creates_matching_local_pair_without_publication(self):
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder)
            report = {"publication_status": "NOT_PUBLISHED"}
            output = preflight.write_local_preflight_outputs(
                dest, b"fixture-only", report
            )
            self.assertEqual(output, dest / "preflight.json")
            self.assertEqual((dest / "index.html").read_bytes(), b"fixture-only")
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), report)

    def test_existing_candidate_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder)
            (dest / "index.html").write_bytes(b"original-bytes")
            with self.assertRaisesRegex(preflight.PreflightError, "refusing overwrite"):
                preflight.write_local_preflight_outputs(dest, b"new", {})
            self.assertEqual((dest / "index.html").read_bytes(), b"original-bytes")
            self.assertFalse((dest / "preflight.json").exists())

    def test_race_existing_html_is_rejected_even_if_precheck_misses(self):
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder)
            (dest / "index.html").write_bytes(b"keep-me")
            with patch.object(Path, "exists", return_value=False):
                with self.assertRaises(FileExistsError):
                    preflight.write_local_preflight_outputs(dest, b"replace-me", {})
            self.assertEqual((dest / "index.html").read_bytes(), b"keep-me")

    def test_race_existing_json_preserved_and_new_html_rolled_back(self):
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder)
            (dest / "preflight.json").write_text("keep-me", encoding="utf-8")
            with patch.object(Path, "exists", return_value=False):
                with self.assertRaises(FileExistsError):
                    preflight.write_local_preflight_outputs(dest, b"temporary", {})
            self.assertEqual((dest / "preflight.json").read_text(encoding="utf-8"),
                             "keep-me")
            self.assertFalse((dest / "index.html").exists())

    def test_json_write_failure_cleans_both_new_local_files(self):
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder)
            with patch.object(preflight.json, "dump", side_effect=OSError("disk-full")):
                with self.assertRaisesRegex(OSError, "disk-full"):
                    preflight.write_local_preflight_outputs(dest, b"temporary", {})
            self.assertFalse((dest / "index.html").exists())
            self.assertFalse((dest / "preflight.json").exists())



if __name__ == "__main__":
    unittest.main()
