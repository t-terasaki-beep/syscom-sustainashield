"""No network or production operations; exact-byte regression tests."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "verify_live_analytics_postdeploy.py"
spec = importlib.util.spec_from_file_location("verify_p0", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fixture():
    tail = b"</script>\n</body></html>\n"
    head = b"<html><body><h1>Example</h1>"
    base = head + b"x" * (25186 - len(head) - len(tail)) + tail
    patched = base.replace(b"</body>", m.TAG + b"</body>")
    return base, patched


class VerifyTests(unittest.TestCase):
    def test_expected_size_and_one_line(self):
        base, patched = fixture()
        self.assertEqual(len(patched), m.PATCHED_SIZE)
        self.assertTrue(patched.endswith(m.TARGET_FOOTER))
        old = m.ORIGINAL_SHA256
        try:
            m.ORIGINAL_SHA256 = m.sha256(base)
            result = m.check_target(patched, "new-etag")
            self.assertEqual(result["analytics_tag_count"], 1)
            self.assertEqual(result["original_restored_sha256"], m.sha256(base))
        finally:
            m.ORIGINAL_SHA256 = old

    def test_no_script_fails(self):
        base, _ = fixture()
        with self.assertRaises(m.VerificationError):
            m.check_target(base, "new-etag")

    def test_duplicate_tag_fails(self):
        _, patched = fixture()
        with self.assertRaises(m.VerificationError):
            m.check_target(patched.replace(m.TAG, m.TAG + m.TAG), "new-etag")

    def test_wrong_etag_fails(self):
        _, patched = fixture()
        with self.assertRaisesRegex(m.VerificationError, "Old ETag"):
            m.check_target(patched, m.ORIGINAL_ETAG)

    def test_mutated_same_size_fails(self):
        base, patched = fixture()
        old = m.ORIGINAL_SHA256
        try:
            m.ORIGINAL_SHA256 = m.sha256(base)
            mutated = patched.replace(b"Example", b"ExAmple", 1)
            with self.assertRaisesRegex(m.VerificationError, "beyond"):
                m.check_target(mutated, "new-etag")
        finally:
            m.ORIGINAL_SHA256 = old

    def test_sibling_unchanged_and_tag_once(self):
        sib = b"<h1>Sibling</h1>" + m.TAG
        res = m.check_sibling(sib, "sibling-etag", m.sha256(sib))
        self.assertEqual(res["status"], "PASS")

    def test_sibling_changed_fails(self):
        sib = b"<h1>Sibling</h1>" + m.TAG
        with self.assertRaisesRegex(m.VerificationError, "changed"):
            m.check_sibling(sib + b"x", "sibling-etag", m.sha256(sib))

    def test_sibling_missing_tag_fails(self):
        sib = b"<h1>Sibling</h1>"
        with self.assertRaisesRegex(m.VerificationError, "tag"):
            m.check_sibling(sib, "sibling-etag", m.sha256(sib))

    def test_etag_validator(self):
        self.assertEqual(m.strong_etag('"6262-65f3790c0687e"'), m.ORIGINAL_ETAG)
        for v in (None, "", 'W/"123"', "123", '"bad"noise'):
            with self.subTest(v=v), self.assertRaises(m.VerificationError):
                m.strong_etag(v)

    def test_live_analytics_asset_id_present(self):
        asset = b"window.ssAnalytics={measurementId:'G-ELZG7B45NH'};"
        result = m.check_analytics_asset(asset)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["sha256"], m.sha256(asset))
        self.assertTrue(result["ga4_measurement_id_present"])
        self.assertFalse(result["ga4_event_receipt_verified"])

    def test_analytics_asset_html_fallback_fails(self):
        with self.assertRaisesRegex(m.VerificationError, "HTML"):
            m.check_analytics_asset(b"  <!DOCTYPE html><title>Fallback</title>G-ELZG7B45NH")

    def test_analytics_asset_wrong_measurement_id_fails(self):
        with self.assertRaisesRegex(m.VerificationError, "expected GA4 ID"):
            m.check_analytics_asset(b"gtag('config', 'G-OTHER')")

    def test_analytics_asset_empty_and_oversize_fail(self):
        for asset in (b"", b"z" * (m.ANALYTICS_ASSET_MAX_BYTES + 1)):
            with self.subTest(size=len(asset)), self.assertRaises(m.VerificationError):
                m.check_analytics_asset(asset)

    def test_bad_sibling_hash_fails(self):
        with self.assertRaises(m.VerificationError):
            m.check_sibling(b"x", "etag", "bad")


if __name__ == "__main__":
    unittest.main()
