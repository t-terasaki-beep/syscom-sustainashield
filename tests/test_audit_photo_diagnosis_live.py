"""Offline tests. No live network operations."""
import io
from email.message import Message
from pathlib import Path
import sys
import unittest
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_photo_diagnosis_live import collect, inspect, NoRedirect, URLS


class FakeResponse:
    status = 200

    def __init__(self, data, headers=None):
        self.data = io.BytesIO(data)
        self.headers = Message()
        for k, v in (headers or {}).items():
            self.headers[k] = v

    def read(self, n=-1):
        return self.data.read(n)

    def getcode(self):
        return self.status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class StaticOpener:
    def __init__(self, results):
        self.results = list(results)
        self.calls = []

    def open(self, req, timeout=None):
        self.calls.append((req.full_url, req.get_method()))
        response = self.results.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class AuditTests(unittest.TestCase):
    def test_identical_pages_measured_from_bytes(self):
        data = (b'<html><head><link rel="canonical" href="/photo-diagnosis/">'
                b'<title>Photo</title><meta name="robots" content="index,follow">'
                b'</head><body><script src="/assets/ss-analytics.js" defer></script></body></html>')
        opener = StaticOpener([FakeResponse(data), FakeResponse(data)])
        report = collect(opener)
        self.assertEqual(report["status"], "observed_both_200")
        self.assertTrue(report["same_body_sha256_if_both_200"])
        self.assertEqual(report["urls"][0]["body_bytes"], len(data))
        self.assertEqual(report["urls"][0]["canonical_links"], ["/photo-diagnosis/"])
        self.assertEqual(report["urls"][0]["ss_analytics_script_count"], 1)
        self.assertEqual(opener.calls, [(URLS[0], "GET"), (URLS[1], "GET")])

    def test_redirect_is_recorded_without_following(self):
        headers = Message()
        headers["Location"] = "/photo-diagnosis/"
        redirect = HTTPError(URLS[1], 301, "Moved Permanently", headers, io.BytesIO(b"redirect"))
        opener = StaticOpener([FakeResponse(b"<html>ok</html>"), redirect])
        report = collect(opener)
        self.assertIsNone(report["same_body_sha256_if_both_200"])
        self.assertEqual(report["urls"][1]["http_status"], 301)
        self.assertEqual(report["urls"][1]["location"], "/photo-diagnosis/")
        self.assertNotIn("sha256", report["urls"][1])
        self.assertEqual(len(opener.calls), 2)

    def test_different_content_not_false_duplicate(self):
        opener = StaticOpener([FakeResponse(b"A"), FakeResponse(b"B")])
        self.assertFalse(collect(opener)["same_body_sha256_if_both_200"])

    def test_max_size_fails_closed(self):
        opener = StaticOpener([FakeResponse(b"12345")])
        entry = inspect(opener, URLS[0], max_bytes=3)
        self.assertIn("exceeds", entry["error"])
        self.assertNotIn("sha256", entry)

    def test_redirect_handler_rejects_all_followups(self):
        self.assertIsNone(NoRedirect().redirect_request(None, None, 302, "Move", {}, "https://unrelated.example/"))


if __name__ == "__main__":
    unittest.main()
