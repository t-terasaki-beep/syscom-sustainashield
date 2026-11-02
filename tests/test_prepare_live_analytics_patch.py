"""Offline tests. No network, credentials, FTP, or publication."""
import importlib.util
from pathlib import Path
import unittest

MOD_PATH = Path(__file__).resolve().parents[1] / "tools" / "prepare_live_analytics_patch.py"
spec = importlib.util.spec_from_file_location("preflight", MOD_PATH)
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)


def sample() -> bytes:
    tail = b"</script></body></html>"
    head = b"<html><body><main><h1>Example</h1>"
    return head + b"x" * (preflight.EXPECTED_ORIGINAL_SIZE - len(head) - len(tail)) + tail


class PatchTests(unittest.TestCase):
    def test_insertion_is_exactly_one_tag(self):
        raw = sample()
        edited = preflight.build_one_line_patch(raw)
        self.assertEqual(len(edited), 25239)
        self.assertEqual(edited.replace(preflight.TAG, b""), raw)
        self.assertEqual(edited.count(preflight.TAG), 1)

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
        raw = sample().replace(b"</script></body></html>", b"</script></boDY></html>")
        with self.assertRaises(preflight.PreflightError):
            preflight.build_one_line_patch(raw)

    def test_etag_weak_or_missing_is_rejected(self):
        for value in (None, 'W/"6262-65f3790c0687e"'):
            with self.assertRaises(preflight.PreflightError):
                preflight.normalize_etag(value)
        self.assertEqual(preflight.normalize_etag('"6262-65f3790c0687e"'),
                         preflight.EXPECTED_ETAG)


if __name__ == "__main__":
    unittest.main()
