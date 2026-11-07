#!/usr/bin/env python3
"""Offline tests: sitemap alias inventory cannot silently infer a canonical."""
import io
import sys
import unittest
from pathlib import Path
from urllib.error import HTTPError, URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_diagnosis_sitemap import (  # noqa: E402
    ALIAS_URL, DESTINATION_URL, SITEMAP_URL, NoRedirect, probe
)


class FakeResponse:
    def __init__(self, body=b"", status=200, mime="application/xml", url=SITEMAP_URL):
        self.body, self.status, self.code, self.url = body, status, status, url
        self.headers = {"Content-Type": mime}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def geturl(self):
        return self.url

    def read(self, amount):
        return self.body[:amount]


class FakeOpener:
    def __init__(self, response):
        self.response, self.calls = response, []

    def open(self, req, timeout=None):
        self.calls.append((req.full_url, req.get_method()))
        if isinstance(self.response, BaseException):
            raise self.response
        return self.response


def urlset(*urls):
    return ('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + ''.join('<url><loc>' + url + '</loc></url>' for url in urls)
            + '</urlset>').encode()


class SitemapAliasTests(unittest.TestCase):
    def test_301_alias_in_urlset_is_review_not_an_automatic_change(self):
        opener = FakeOpener(FakeResponse(urlset(ALIAS_URL, DESTINATION_URL)))
        result = probe(opener)
        self.assertEqual(result["verdict"], "REVIEW_301_ALIAS_LISTED_IN_SITEMAP")
        self.assertTrue(result["redirect_alias_listed"])
        self.assertTrue(result["destination_listed"])
        self.assertFalse(result["sitemap_modified"])
        self.assertFalse(result["search_console_submission"])
        self.assertEqual(opener.calls, [(SITEMAP_URL, "GET")])

    def test_alias_absent_only_applies_to_current_urlset(self):
        result = probe(FakeOpener(FakeResponse(urlset(DESTINATION_URL))))
        self.assertEqual(result["verdict"], "ALIAS_NOT_LISTED_IN_THIS_URLSET")
        self.assertFalse(result["redirect_alias_listed"])
        self.assertTrue(result["canonical_policy"].startswith("HOLD"))

    def test_sitemap_index_is_unknown_not_alias_absent(self):
        xml = b'<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>https://syscom-sustaina-shield.com/child.xml</loc></sitemap></sitemapindex>'
        opener = FakeOpener(FakeResponse(xml))
        result = probe(opener)
        self.assertEqual(result["verdict"], "UNVERIFIED_SITEMAP_INDEX_OR_OTHER_ROOT")
        self.assertNotIn("redirect_alias_listed", result)
        self.assertEqual(len(opener.calls), 1)  # no unapproved child sitemap GET

    def test_redirect_status_is_not_followed(self):
        opener = FakeOpener(HTTPError(SITEMAP_URL, 301, "Moved", {"Location": "https://outside.example/"}, io.BytesIO()))
        result = probe(opener)
        self.assertEqual(result["verdict"], "UNVERIFIED_SITEMAP_HTTP")
        self.assertEqual(len(opener.calls), 1)
        self.assertIsNone(NoRedirect().redirect_request(None, None, 301, "Moved", {}, "https://outside.example/"))

    def test_network_failure_is_unknown_not_empty(self):
        result = probe(FakeOpener(URLError("DNS down")))
        self.assertEqual(result["verdict"], "UNVERIFIED_SITEMAP_NETWORK")
        self.assertNotIn("redirect_alias_listed", result)

    def test_invalid_xml_and_wrong_mime_do_not_claim_absence(self):
        for body, mime, expected in (
            (b'<urlset><url>', "application/xml", "UNVERIFIED_SITEMAP_XML_INVALID"),
            (urlset(DESTINATION_URL), "text/html", "UNVERIFIED_SITEMAP_MIME"),
        ):
            with self.subTest(expected=expected):
                self.assertEqual(probe(FakeOpener(FakeResponse(body, mime=mime)))["verdict"], expected)


if __name__ == "__main__":
    unittest.main()
