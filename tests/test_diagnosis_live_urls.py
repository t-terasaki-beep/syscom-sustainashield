#!/usr/bin/env python3
"""Offline, network-free tests for safe diagnosis alias HTTP evidence."""
import hashlib
import io
import sys
import unittest
from pathlib import Path
from urllib.error import HTTPError, URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from inspect_diagnosis_live_urls import (  # noqa: E402
    BASE, NoRedirect, inspect_one, snapshot
)


class FakeResponse:
    def __init__(self, url, status=200, body=b"", headers=None):
        self.url, self.status, self.body = url, status, body
        self.headers = headers or {"Content-Type": "text/html"}
        self.code = status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def geturl(self):
        return self.url

    def read(self, size=-1):
        return self.body[:size]


class FakeOpener:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def open(self, request, timeout=None):
        self.calls.append((request.full_url, request.get_method(), timeout))
        response = self.responses.pop(0)
        if isinstance(response, BaseException):
            raise response
        return response


class DiagnosisLiveAliasTests(unittest.TestCase):
    def test_200_extracts_canonical_and_robots_but_no_decision(self):
        data = (b'<html><head><link rel="alternate canonical" '
                b'href="https://syscom-sustaina-shield.com/photo-diagnosis/">'
                b'<meta name="robots" content="index,follow"></head></html>')
        opener = FakeOpener([FakeResponse(BASE + "/photo-diagnosis/", body=data,
                                          headers={"Content-Type": "text/html; charset=utf-8",
                                                   "ETag": '"a"'})])
        result = inspect_one("/photo-diagnosis/", opener)
        self.assertEqual(result["status"], 200)
        self.assertEqual(result["bytes"], len(data))
        self.assertEqual(result["sha256"], hashlib.sha256(data).hexdigest())
        self.assertEqual(result["canonical_links"], [BASE + "/photo-diagnosis/"])
        self.assertEqual(result["meta_robots"], ["index,follow"])
        self.assertEqual(opener.calls[0][1], "GET")

    def test_redirect_status_and_location_are_preserved_without_following(self):
        url = BASE + "/shindan.html"
        err = HTTPError(url, 301, "Moved", {"Location": "/photo-diagnosis/"}, io.BytesIO(b""))
        opener = FakeOpener([err])
        result = inspect_one("/shindan.html", opener)
        self.assertEqual(result["status"], 301)
        self.assertEqual(result["location"], "/photo-diagnosis/")
        self.assertFalse(result["body_examined"])
        self.assertFalse(result["redirect_followed"])
        self.assertEqual(len(opener.calls), 1)
        self.assertIsNone(NoRedirect().redirect_request(None, None, 301, "Moved", {}, url))

    def test_same_content_does_not_claim_canonical_decision(self):
        data = b"<html><head></head><body>same</body></html>"
        opener = FakeOpener([
            FakeResponse(BASE + "/photo-diagnosis/", body=data),
            FakeResponse(BASE + "/shindan.html", body=data),
        ])
        report = snapshot(opener)
        self.assertTrue(report["same_body_sha256_if_both_200"])
        self.assertFalse(report["external_backlinks_checked"])
        self.assertFalse(report["search_console_checked"])
        self.assertTrue(report["canonical_decision"].startswith("HOLD"))
        self.assertEqual(len(opener.calls), 2)

    def test_network_failure_is_unknown_not_a_negative_redirect_proof(self):
        opener = FakeOpener([URLError("DNS lookup unavailable")])
        row = inspect_one("/shindan.html", opener)
        self.assertIsNone(row["status"])
        self.assertEqual(row["observation"], "unavailable_not_zero")

    def test_unapproved_urls_never_generate_requests(self):
        opener = FakeOpener([])
        with self.assertRaises(ValueError):
            inspect_one("/contact.html", opener)
        self.assertEqual(opener.calls, [])

    def test_mismatched_body_is_not_marked_as_duplicate(self):
        opener = FakeOpener([
            FakeResponse(BASE + "/photo-diagnosis/", body=b"<html>first</html>"),
            FakeResponse(BASE + "/shindan.html", body=b"<html>second</html>"),
        ])
        report = snapshot(opener)
        self.assertFalse(report["same_body_sha256_if_both_200"])


    def test_expected_301_target_is_only_an_observation(self):
        target = BASE + "/photo-diagnosis/"
        alias = BASE + "/shindan.html"
        opener = FakeOpener([
            FakeResponse(target, body=b"<html><head></head></html>"),
            HTTPError(alias, 301, "Moved", {"Location": target}, io.BytesIO(b"")),
        ])
        report = snapshot(opener)
        self.assertEqual(report["redirect_integrity_observation"], "OBSERVED_301_TO_200_TARGET")
        self.assertFalse(report["search_console_checked"])
        self.assertTrue(report["canonical_decision"].startswith("HOLD"))
        self.assertEqual(len(opener.calls), 2)

    def test_relative_redirect_is_accepted_but_external_location_is_flagged(self):
        target = BASE + "/photo-diagnosis/"
        alias = BASE + "/shindan.html"
        target_page = FakeResponse(target, body=b"<html></html>")
        relative = snapshot(FakeOpener([
            target_page,
            HTTPError(alias, 301, "Moved", {"Location": "/photo-diagnosis/"}, io.BytesIO(b"")),
        ]))
        self.assertEqual(relative["redirect_integrity_observation"], "OBSERVED_301_TO_200_TARGET")
        external = snapshot(FakeOpener([
            target_page,
            HTTPError(alias, 301, "Moved", {"Location": "https://other.example/photo-diagnosis/"}, io.BytesIO(b"")),
        ]))
        self.assertEqual(external["redirect_integrity_observation"], "REVIEW_REDIRECT_TARGET")

    def test_network_failure_cannot_be_construed_as_redirect_absence(self):
        report = snapshot(FakeOpener([
            FakeResponse(BASE + "/photo-diagnosis/", body=b"<html></html>"),
            URLError("DNS unavailable"),
        ]))
        self.assertEqual(report["redirect_integrity_observation"], "UNVERIFIED_FETCH")
        self.assertEqual(report["routes"][1]["observation"], "unavailable_not_zero")

    def test_conflicting_canonical_tag_triggers_review(self):
        target = BASE + "/photo-diagnosis/"
        alias = BASE + "/shindan.html"
        page = (b'<html><head><link rel="canonical" href="'
                + (BASE + "/shindan.html").encode("ascii") + b'"></head></html>')
        report = snapshot(FakeOpener([
            FakeResponse(target, body=page),
            HTTPError(alias, 301, "Moved", {"Location": target}, io.BytesIO(b"")),
        ]))
        self.assertEqual(report["redirect_integrity_observation"], "REVIEW_CONFLICTING_CANONICAL")


    def test_target_noindex_in_meta_or_header_requires_review(self):
        target, alias = BASE + "/photo-diagnosis/", BASE + "/shindan.html"
        cases = [
            ("meta", b'<meta name="robots" content="noindex,follow">', {}),
            ("x-robots", b'<html></html>',
             {"Content-Type": "text/html", "X-Robots-Tag": "googlebot: noindex"}),
            ("none", b'<html></html>',
             {"Content-Type": "text/html", "X-Robots-Tag": "none"}),
        ]
        for label, html, headers in cases:
            with self.subTest(case=label):
                report = snapshot(FakeOpener([
                    FakeResponse(target, body=html, headers=headers),
                    HTTPError(alias, 301, "Moved", {"Location": target}, io.BytesIO(b"")),
                ]))
                self.assertEqual(report["redirect_integrity_observation"],
                                 "REVIEW_TARGET_NOINDEX")
                self.assertTrue(report["canonical_decision"].startswith("HOLD"))

    def test_googlebot_specific_meta_noindex_requires_review(self):
        target, alias = BASE + "/photo-diagnosis/", BASE + "/shindan.html"
        page = (b'<meta name="robots" content="index,follow">'
                b'<meta name="GoOgLeBoT" content="noindex,follow">')
        report = snapshot(FakeOpener([
            FakeResponse(target, body=page),
            HTTPError(alias, 301, "Moved", {"Location": target}, io.BytesIO(b"")),
        ]))
        self.assertEqual(report["redirect_integrity_observation"], "REVIEW_TARGET_NOINDEX")
        self.assertIn("noindex,follow", report["routes"][0]["meta_robots"])

    def test_googlebot_image_noindex_does_not_block_html_page(self):
        target, alias = BASE + "/photo-diagnosis/", BASE + "/shindan.html"
        page = (b'<meta name="robots" content="index,follow">'
                b'<meta name="googlebot-image" content="noindex">')
        report = snapshot(FakeOpener([
            FakeResponse(target, body=page),
            HTTPError(alias, 301, "Moved", {"Location": target}, io.BytesIO(b"")),
        ]))
        self.assertEqual(report["redirect_integrity_observation"], "OBSERVED_301_TO_200_TARGET")

    def test_nofollow_and_noindexing_substrings_are_not_noindex(self):
        target, alias = BASE + "/photo-diagnosis/", BASE + "/shindan.html"
        page = b'<meta name="robots" content="index,nofollow">'
        report = snapshot(FakeOpener([
            FakeResponse(target, body=page, headers={
                "Content-Type": "text/html", "X-Robots-Tag": "noindexing"
            }),
            HTTPError(alias, 301, "Moved", {"Location": target}, io.BytesIO(b"")),
        ]))
        self.assertEqual(report["redirect_integrity_observation"], "OBSERVED_301_TO_200_TARGET")


if __name__ == "__main__":
    unittest.main()
