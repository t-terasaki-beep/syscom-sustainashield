"""No network or production operations; exact-byte regression tests."""
import importlib.util
import json
import os
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

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
    def test_article_mime_accepts_html_and_rejects_non_html(self):
        for mime in ("text/html", "TEXT/HTML; charset=UTF-8", "application/xhtml+xml"):
            m.require_html_media_type(mime)
        for mime in (None, "", "text/plain", "text/javascript", "application/octet-stream"):
            with self.subTest(mime=mime), self.assertRaisesRegex(
                m.VerificationError, "Content-Type is not HTML"
            ):
                m.require_html_media_type(mime)

    def test_postdeploy_fetch_rejects_plain_text_before_hash_comparison(self):
        class FakeResponse:
            status = 200
            headers = {"ETag": '"new-etag"', "Content-Type": "text/plain"}
            def __enter__(self):
                return self
            def __exit__(self, *_):
                return False
            def geturl(self):
                return m.TARGET
            def read(self, *_):
                raise AssertionError("Must reject non-HTML before reading")

        with patch.object(m, "urlopen", return_value=FakeResponse()):
            with self.assertRaisesRegex(m.VerificationError, "Content-Type is not HTML"):
                m.fetch_exact(m.TARGET, 25300)

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

    def test_production_completed_html_sha_pin_accepts_exact_candidate(self):
        base, patched = fixture()
        source_sha = m.sha256(base)
        with patch.object(m, "ORIGINAL_SHA256", source_sha), \
             patch.object(m, "PRODUCTION_ORIGINAL_SHA256", source_sha), \
             patch.object(m, "APPROVED_PATCHED_SHA256", m.sha256(patched)):
            result = m.check_target(patched, "new-etag")
        self.assertEqual(result["sha256"], m.sha256(patched))

    def test_production_completed_html_wrong_approved_sha_stops(self):
        # Even if the restored original SHA matches, the independently pinned
        # completed-file digest is a mandatory separate publication criterion.
        base, patched = fixture()
        source_sha = m.sha256(base)
        with patch.object(m, "ORIGINAL_SHA256", source_sha), \
             patch.object(m, "PRODUCTION_ORIGINAL_SHA256", source_sha), \
             patch.object(m, "APPROVED_PATCHED_SHA256", "0" * 64):
            with self.assertRaisesRegex(m.VerificationError, "approved SHA-256"):
                m.check_target(patched, "new-etag")

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

    def test_modified_sibling_cannot_be_approved_by_its_own_postchange_hash(self):
        # An operator accidentally capturing the baseline AFTER publication
        # must not make a modified sibling pass the non-destruction gate.
        modified = b"<h1>Changed sibling</h1>" + m.TAG
        supplied_after_change = m.sha256(modified)
        self.assertNotEqual(supplied_after_change, m.SIBLING_APPROVED_SHA256)
        with self.assertRaisesRegex(m.VerificationError, "independently approved"):
            m.check_sibling(modified, "sibling-etag", supplied_after_change)

    def test_sibling_unchanged_and_tag_once(self):
        sib = b"<h1>Sibling</h1>" + m.TAG
        with patch.object(m, "SIBLING_APPROVED_SHA256", m.sha256(sib)):
            res = m.check_sibling(sib, "sibling-etag", m.sha256(sib))
        self.assertEqual(res["status"], "PASS")

    def test_sibling_changed_fails(self):
        sib = b"<h1>Sibling</h1>" + m.TAG
        with patch.object(m, "SIBLING_APPROVED_SHA256", m.sha256(sib)):
            with self.assertRaisesRegex(m.VerificationError, "changed"):
                m.check_sibling(sib + b"x", "sibling-etag", m.sha256(sib))

    def test_sibling_missing_tag_fails(self):
        sib = b"<h1>Sibling</h1>"
        with patch.object(m, "SIBLING_APPROVED_SHA256", m.sha256(sib)):
            with self.assertRaisesRegex(m.VerificationError, "tag"):
                m.check_sibling(sib, "sibling-etag", m.sha256(sib))

    def test_etag_validator(self):
        self.assertEqual(m.strong_etag('"6262-65f3790c0687e"'), m.ORIGINAL_ETAG)
        for v in (None, "", 'W/"123"', "123", '"bad"noise'):
            with self.subTest(v=v), self.assertRaises(m.VerificationError):
                m.strong_etag(v)

    def test_live_analytics_asset_id_present(self):
        asset = b"window.ssAnalytics={measurementId:'G-ELZG7B45NH'};"
        with patch.object(m, "ANALYTICS_ASSET_EXPECTED_SIZE", len(asset)), \
             patch.object(m, "ANALYTICS_ASSET_EXPECTED_SHA256", m.sha256(asset)):
            result = m.check_analytics_asset(asset, "text/javascript; charset=utf-8")
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["sha256"], m.sha256(asset))
        self.assertTrue(result["ga4_measurement_id_present"])
        self.assertEqual(result["javascript_content_type"], "text/javascript")
        self.assertFalse(result["ga4_event_receipt_verified"])

    def test_analytics_asset_html_fallback_fails(self):
        with self.assertRaisesRegex(m.VerificationError, "HTML"):
            m.check_analytics_asset(b"  <!DOCTYPE html><title>Fallback</title>G-ELZG7B45NH", "text/javascript")

    def test_analytics_asset_wrong_measurement_id_fails(self):
        with self.assertRaisesRegex(m.VerificationError, "expected GA4 ID"):
            m.check_analytics_asset(b"gtag('config', 'G-OTHER')", "application/javascript")

    def test_analytics_asset_empty_and_oversize_fail(self):
        for asset in (b"", b"z" * (m.ANALYTICS_ASSET_MAX_BYTES + 1)):
            with self.subTest(size=len(asset)), self.assertRaises(m.VerificationError):
                m.check_analytics_asset(asset, "text/javascript")

    def test_analytics_asset_wrong_or_missing_mime_fails(self):
        js = b"// G-ELZG7B45NH"
        for mime in (None, "", "text/html; charset=utf-8", "text/plain",
                     "application/octet-stream", "image/svg+xml"):
            with self.subTest(mime=mime), self.assertRaisesRegex(m.VerificationError, "Content-Type"):
                m.check_analytics_asset(js, mime)

    def test_analytics_asset_javascript_mime_variants_pass(self):
        js = b"// G-ELZG7B45NH"
        for mime in ("text/javascript", "TEXT/JAVASCRIPT; charset=UTF-8",
                     "application/javascript; charset=utf-8", "application/ecmascript"):
            with self.subTest(mime=mime):
                with patch.object(m, "ANALYTICS_ASSET_EXPECTED_SIZE", len(js)), \
                     patch.object(m, "ANALYTICS_ASSET_EXPECTED_SHA256", m.sha256(js)):
                    result = m.check_analytics_asset(js, mime)
                self.assertEqual(result["status"], "PASS")
                self.assertEqual(result["javascript_content_type"], mime.split(";", 1)[0].lower())

    def test_analytics_asset_wrong_sha_fails(self):
        # Same size, same measurement ID, but changed bytes must not pass.
        original = b"// G-ELZG7B45NH; OK"
        changed = b"// G-ELZG7B45NH; NO"
        self.assertEqual(len(original), len(changed))
        with patch.object(m, "ANALYTICS_ASSET_EXPECTED_SIZE", len(original)), \
             patch.object(m, "ANALYTICS_ASSET_EXPECTED_SHA256", m.sha256(original)):
            with self.assertRaisesRegex(m.VerificationError, "SHA-256"):
                m.check_analytics_asset(changed, "text/javascript")

    def test_analytics_asset_wrong_size_fails(self):
        original = b"// G-ELZG7B45NH"
        with patch.object(m, "ANALYTICS_ASSET_EXPECTED_SIZE", len(original) + 1), \
             patch.object(m, "ANALYTICS_ASSET_EXPECTED_SHA256", m.sha256(original)):
            with self.assertRaisesRegex(m.VerificationError, "size differs"):
                m.check_analytics_asset(original, "text/javascript")

    def test_bad_sibling_hash_fails(self):
        with self.assertRaises(m.VerificationError):
            m.check_sibling(b"x", "etag", "bad")


    def test_cli_writes_local_http_evidence_once_without_claiming_ga4_receipt(self):
        base, patched = fixture()
        sibling = b"<h1>Sibling</h1>" + m.TAG
        with tempfile.TemporaryDirectory() as folder:
            evidence_path = Path(folder) / "http_postdeploy.json"
            with patch.object(m, "ORIGINAL_SHA256", m.sha256(base)), \
                 patch.object(m, "SIBLING_APPROVED_SHA256", m.sha256(sibling)), \
                 patch.object(m, "fetch_exact", side_effect=[
                     (patched, "patched-etag"), (sibling, "sibling-etag")
                 ]) as fetch_mock, \
                 patch.object(m, "fetch_analytics_asset", return_value={
                     "status": "PASS", "ga4_event_receipt_verified": False
                 }), \
                 patch("sys.argv", ["verify_live_analytics_postdeploy.py",
                                   "--sibling-before-sha256", m.sha256(sibling),
                                   "--evidence-json", str(evidence_path)]):
                self.assertEqual(m.main(), 0)
                self.assertEqual(fetch_mock.call_count, 2)
            record = json.loads(evidence_path.read_text(encoding="utf-8"))
            self.assertEqual(record["publication_verification"], "PASS_FOR_HTTP_CONTENT_ONLY")
            self.assertFalse(record["ga4_page_view_delivery_verified"])
            self.assertEqual(record["sibling_unchanged"]["sha256"], m.sha256(sibling))
            self.assertIn("observed_at_utc", record)
            self.assertEqual(record["evidence_scope"],
                             "POSTDEPLOY_HTTP_BYTES_ONLY_GA4_EVENT_UNVERIFIED")

    def test_cli_existing_evidence_file_stops_before_network_and_preserves_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            evidence_path = Path(folder) / "http_postdeploy.json"
            evidence_path.write_text("untouched", encoding="utf-8")
            with patch("sys.argv", ["verify_live_analytics_postdeploy.py",
                                   "--sibling-before-sha256", "a" * 64,
                                   "--evidence-json", str(evidence_path)]), \
                 patch.object(m, "fetch_exact") as fetch_mock, \
                 self.assertRaisesRegex(m.VerificationError, "refusing overwrite"):
                m.main()
            fetch_mock.assert_not_called()
            self.assertEqual(evidence_path.read_text(encoding="utf-8"), "untouched")


    def test_evidence_writer_refuses_existing_file_even_after_precheck_race(self):
        # The final open("x"), not the earlier exists(), is the safety gate.
        with tempfile.TemporaryDirectory() as folder:
            evidence_path = Path(folder) / "http_postdeploy.json"
            evidence_path.write_text("another-run", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                m.write_verification_evidence(evidence_path, {"status": "PASS"})
            self.assertEqual(evidence_path.read_text(encoding="utf-8"), "another-run")

    def test_evidence_writer_serializes_before_creating_file(self):
        with tempfile.TemporaryDirectory() as folder:
            evidence_path = Path(folder) / "http_postdeploy.json"
            with self.assertRaises(TypeError):
                m.write_verification_evidence(evidence_path, {"bad": object()})
            self.assertFalse(evidence_path.exists())

    def test_evidence_writer_interrupted_write_removes_partial_file(self):
        with tempfile.TemporaryDirectory() as folder:
            evidence_path = Path(folder) / "http_postdeploy.json"
            real_fdopen = os.fdopen

            class InterruptedWriter:
                def __init__(self, stream):
                    self.stream = stream

                def __enter__(self):
                    self.stream.__enter__()
                    return self

                def __exit__(self, *args):
                    return self.stream.__exit__(*args)

                def write(self, payload):
                    self.stream.write(payload[:8])
                    self.stream.flush()
                    raise OSError("simulated-disk-full")

            def fdopen_with_failure(fd, *args, **kwargs):
                return InterruptedWriter(real_fdopen(fd, *args, **kwargs))

            with patch.object(m.os, "fdopen", fdopen_with_failure):
                with self.assertRaisesRegex(OSError, "simulated-disk-full"):
                    m.write_verification_evidence(evidence_path, {"status": "PASS"})
            self.assertFalse(evidence_path.exists())



    def test_postdeploy_evidence_is_0600_even_with_world_readable_umask(self):
        # Mirrors the private preflight candidate: permissions set at creation.
        if os.name != "posix":
            self.skipTest("POSIX file modes required")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "http_postdeploy.json"
            previous_umask = os.umask(0)
            try:
                m.write_verification_evidence(path, {"status": "PASS"})
            finally:
                os.umask(previous_umask)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["status"], "PASS")

    def test_shared_evidence_directory_stops_before_writing(self):
        if os.name != "posix":
            self.skipTest("POSIX directory modes required")
        with tempfile.TemporaryDirectory() as folder:
            shared = Path(folder) / "shared-evidence"
            shared.mkdir(mode=0o755)
            path = shared / "http_postdeploy.json"
            with self.assertRaisesRegex(m.VerificationError, "operator-owned and private"):
                m.write_verification_evidence(path, {"status": "PASS"})
            self.assertFalse(path.exists())
            self.assertEqual(shared.stat().st_mode & 0o777, 0o755)

    def test_shared_evidence_directory_stops_cli_before_network(self):
        if os.name != "posix":
            self.skipTest("POSIX directory modes required")
        with tempfile.TemporaryDirectory() as folder:
            shared = Path(folder) / "shared-evidence"
            shared.mkdir(mode=0o755)
            path = shared / "http_postdeploy.json"
            with patch("sys.argv", ["verify_live_analytics_postdeploy.py",
                                    "--sibling-before-sha256", "a" * 64,
                                    "--evidence-json", str(path)]), \\
                 patch.object(m, "fetch_exact") as fetch_mock, \\
                 self.assertRaisesRegex(m.VerificationError, "operator-owned and private"):
                m.main()
            fetch_mock.assert_not_called()
            self.assertFalse(path.exists())

    def test_evidence_json_refuses_public_webroots_before_writing(self):
        with tempfile.TemporaryDirectory() as folder:
            for webroot in ("public_html", "WWW", "htdocs", "httpdocs",
                            "wwwroot", "webroot", "public"):
                with self.subTest(webroot=webroot):
                    path = Path(folder) / webroot / "inspection.json"
                    with self.assertRaisesRegex(m.VerificationError, "public web root"):
                        m.write_verification_evidence(path, {"status": "PASS"})
                    self.assertFalse(path.exists())

    def test_evidence_json_refuses_nginx_srv_http_and_dist(self):
        # A successful HTTP inspection is sensitive metadata and must not
        # become a publicly served file through a common alternate webroot.
        with tempfile.TemporaryDirectory() as folder:
            roots = (
                Path(folder) / "usr" / "share" / "nginx" / "html",
                Path(folder) / "srv" / "http",
                Path(folder) / "dist",
            )
            for root in roots:
                path = root / "inspection.json"
                with self.subTest(root=str(root)), self.assertRaisesRegex(
                    m.VerificationError, "public web root"
                ):
                    m.write_verification_evidence(path, {"status": "PASS"})
                self.assertFalse(path.exists())

    def test_evidence_json_symlink_to_webroot_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            webroot = root / "public_html"
            webroot.mkdir()
            alias = root / "private_alias"
            try:
                alias.symlink_to(webroot, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Directory symlinks unavailable")
            with self.assertRaisesRegex(m.VerificationError, "public web root"):
                m.write_verification_evidence(alias / "inspection.json", {"status": "PASS"})
            self.assertFalse((webroot / "inspection.json").exists())

    def test_cli_public_evidence_path_stops_before_network(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "www" / "inspection.json"
            with patch("sys.argv", ["verify_live_analytics_postdeploy.py",
                                   "--sibling-before-sha256", "a" * 64,
                                   "--evidence-json", str(path)]), \
                 patch.object(m, "fetch_exact") as fetch_mock, \
                 self.assertRaisesRegex(m.VerificationError, "public web root"):
                m.main()
            fetch_mock.assert_not_called()
            self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
