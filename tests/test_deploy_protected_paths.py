"""Offline safety checks for production-only paths; no FTP calls or secrets."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

PUBLISH = Path(__file__).resolve().parents[1] / "deploy" / "publish.sh"


class ProtectedRouteTests(unittest.TestCase):
    def check_rejected(self, remote_path: str, expected_message: str, remote_root: str = "/public_html/") -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "deploy").mkdir()
            (root / "input.html").write_text("fixture only", encoding="utf-8")
            manifest = root / "changeset.txt"
            manifest.write_text(f"input.html {remote_path}\n", encoding="utf-8")
            env = os.environ.copy()
            env.update({
                "FTP_HOST": "ftp.invalid.example",
                "FTP_USER": "fixture",
                "FTP_PASS": "fixture",
                "FTP_REMOTE_ROOT": remote_root,
            })
            result = subprocess.run(
                ["bash", str(PUBLISH), str(manifest)],
                cwd=root, env=env, capture_output=True, text=True,
                timeout=5, check=False,
            )
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertIn(expected_message, result.stdout)
            self.assertFalse(list((root / "deploy" / "_runs").rglob("backup/*")))

    def test_production_only_routes_never_publish_from_repo(self):
        for path in (
            "column/chiba-suigai-hinanjo-dengen/index.html",
            "photo-diagnosis/index.html",
            "shindan.html",
        ):
            with self.subTest(path=path):
                self.check_rejected(path, "上書き禁止")

    def test_protected_subtrees_reject_other_filename_and_directory_targets(self):
        # Reject more than index.html: an incidental asset upload into these
        # production-maintained routes must never bypass the repository guard.
        for path in (
            "column/chiba-suigai-hinanjo-dengen",
            "column/chiba-suigai-hinanjo-dengen/new.html",
            "column/chiba-suigai-hinanjo-dengen/assets/app.js",
            "photo-diagnosis",
            "photo-diagnosis/alternate.html",
            "photo-diagnosis/assets/style.css",
        ):
            with self.subTest(path=path):
                self.check_rejected(path, "上書き禁止")

    def test_document_root_prefixes_cannot_bypass_protection(self):
        # FTP_REMOTE_ROOT can be "/" rather than "/public_html/".
        # The manifest can therefore embed a document-root folder. This still
        # targets the protected live page and must never reach the network.
        for path in (
            "public_html/column/chiba-suigai-hinanjo-dengen/index.html",
            "public_html/photo-diagnosis/index.html",
            "public_html/shindan.html",
            "www/column/chiba-suigai-hinanjo-dengen/assets/tracker.js",
            "httpdocs/photo-diagnosis",
            "site/legacy/shindan.html",
        ):
            with self.subTest(path=path):
                self.check_rejected(path, "上書き禁止")

    def test_protected_destination_cannot_hide_inside_ftp_remote_root(self):
        # Even a manifest containing only index.html targets the production
        # article when FTP_REMOTE_ROOT points directly at its directory.
        # The guard must stop before any FTP request or backup attempt.
        for root, path in (
            ("/column/chiba-suigai-hinanjo-dengen/", "index.html"),
            ("/public_html/column/chiba-suigai-hinanjo-dengen/", "index.html"),
            ("/public_html/photo-diagnosis/", "index.html"),
            ("/site/legacy/shindan.html/", "index.html"),
        ):
            with self.subTest(root=root, path=path):
                self.check_rejected(path, "上書き禁止", remote_root=root)

    def test_ambiguous_ftp_remote_root_is_rejected_pre_network(self):
        # Dot segments, URL encodings, and double slashes can be normalized
        # by the FTP server AFTER an innocent-looking manifest is checked.
        for root in (
            "/public_html/column/other/../chiba-suigai-hinanjo-dengen/",
            "/public_html/photo-diagnosis/./",
            "/public_html%2Fcolumn/chiba-suigai-hinanjo-dengen/",
            "/public_html//column/chiba-suigai-hinanjo-dengen/",
            "public_html/column/chiba-suigai-hinanjo-dengen/",
        ):
            with self.subTest(root=root):
                self.check_rejected("index.html", "FTP_REMOTE_ROOT", remote_root=root)

    def test_url_encoded_and_url_suffix_aliases_rejected(self):
        # A remote server or intermediary can decode URL syntax differently.
        # Reject these ambiguous forms rather than risk bypassing protected paths.
        for path in (
            "shindan%2ehtml",
            "photo-diagnosis%2findex.html",
            "column/chiba-suigai-hinanjo-dengen%2Findex.html",
            "column%2Fchiba-suigai-hinanjo-dengen/index.html",
            "column\\\\chiba-suigai-hinanjo-dengen\\\\index.html",
            "shindan.html?rev=2",
            "shindan.html#v1",
            "column/..",
            "column/.",
        ):
            with self.subTest(path=path):
                self.check_rejected(path, "非正規")

    def test_crlf_and_embedded_carriage_returns_stop_before_ftp(self):
        # A Windows changeset may carry CRLF. Without an explicit CR check,
        # the remote filename is parsed as shindan.html\\r and bypasses
        # exact protected-route matching. Reject all CR, even on benign paths.
        for path in (
            "shindan.html\\r",
            "photo-diagnosis/index.html\\r",
            "ordinary.html\\r",
            "column/chiba-suigai-hinanjo-dengen/\\rindex.html",
        ):
            with self.subTest(path=repr(path)):
                self.check_rejected(path.replace("\\r", "\r"), "CR 制御文字")

    def test_noncanonical_remote_paths_rejected(self):
        for path in (
            "./shindan.html",
            "column/../shindan.html",
            "/shindan.html",
            "column//chiba-suigai-hinanjo-dengen/index.html",
        ):
            with self.subTest(path=path):
                self.check_rejected(path, "非正規")


if __name__ == "__main__":
    unittest.main()
