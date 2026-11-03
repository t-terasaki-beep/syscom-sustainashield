"""Offline safety checks for production-only paths; no FTP calls or secrets."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

PUBLISH = Path(__file__).resolve().parents[1] / "deploy" / "publish.sh"


class ProtectedRouteTests(unittest.TestCase):
    def check_rejected(self, remote_path: str, expected_message: str) -> None:
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
                "FTP_REMOTE_ROOT": "/public_html/",
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
