#!/usr/bin/env python3
"""Offline regression tests for allowlisted production inlink inventory."""
import sys
import unittest
from pathlib import Path
from urllib.error import URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_diagnosis_live_inlinks import (  # noqa: E402
    BASE, SITEMAP_URL, count_alias_links, scan,
)


class FakeResponse:
    def __init__(self, url, body=b"", status=200, mime="text/html"):
        self.url, self.body, self.status = url, body, status
        self.headers = {"Content-Type": mime}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def geturl(self):
        return self.url

    def read(self, n):
        return self.body[:n]


class FakeOpener:
    def __init__(self, records):
        self.records, self.calls = records, []

    def open(self, req, timeout=15):
        url = req.full_url
        self.calls.append((url, req.get_method()))
        item = self.records[url]
        if isinstance(item, BaseException):
            raise item
        return item


def sitemap(*urls):
    return ('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + ''.join('<url><loc>' + u + '</loc></url>' for u in urls)
            + '</urlset>').encode("utf-8")


class LiveInlinkTests(unittest.TestCase):
    def test_only_same_site_anchor_links_are_counted(self):
        a, b = BASE + "/a", BASE + "/b"
        html_a = (b'<html><a href="/shindan.html">old</a>'
                  b'<a href="https://syscom-sustaina-shield.com/photo-diagnosis/#step">new</a>'
                  b'<a href="https://external.example/shindan.html">offsite</a>'
                  b'<link rel="canonical" href="/shindan.html"></html>')
        html_b = b'<html><a href="shindan.html?source=campaign">relative</a></html>'
        opener = FakeOpener({
            SITEMAP_URL: FakeResponse(SITEMAP_URL, sitemap(a, b), mime="application/xml"),
            a: FakeResponse(a, html_a),
            b: FakeResponse(b, html_b),
        })
        result = scan(opener)
        self.assertEqual(result["verdict"], "COMPLETE_SITEMAP_HTML_INVENTORY_NO_CANONICAL_DECISION")
        self.assertEqual(result["scanned_html_pages"], 2)
        self.assertEqual(result["targets"]["/shindan.html"]["occurrences"], 2)
        self.assertEqual(result["targets"]["/photo-diagnosis/"]["occurrences"], 1)
        self.assertFalse(result["external_backlinks_checked"])
        self.assertFalse(result["production_modified"])
        self.assertEqual(len(opener.calls), 3)
        self.assertTrue(all(method == "GET" for _, method in opener.calls))

    def test_first_base_href_controls_relative_inlinks(self):
        # Browser document.baseURI follows the first href-bearing <base>.
        # A relative link is not necessarily relative to its sitemap URL.
        src = BASE + "/articles/overview/"
        html = (b'<a href="shindan.html">alias</a>'
                b'<base href="/"><a href="photo-diagnosis/#one">new</a>'
                b'<base href="https://outside.example/">ignored</base>')
        counts = count_alias_links(src, html)
        self.assertEqual(counts["/shindan.html"], 1)
        self.assertEqual(counts["/photo-diagnosis/"], 1)

    def test_offsite_base_does_not_create_false_internal_links(self):
        # Root-relative hrefs also resolve against the <base> origin.
        src = BASE + "/"
        html = (b'<base href="https://outside.example/sub/">'
                b'<a href="/shindan.html">alias outside</a>'
                b'<a href="photo-diagnosis/">diagnosis outside</a>'
                b'<a href="https://syscom-sustaina-shield.com/photo-diagnosis/">absolute internal</a>')
        counts = count_alias_links(src, html)
        self.assertEqual(counts["/shindan.html"], 0)
        self.assertEqual(counts["/photo-diagnosis/"], 1)

    def test_empty_first_base_is_effective_and_later_base_ignored(self):
        # An empty first base href means the page URL; later bases are ignored.
        src = BASE + "/"
        html = (b'<base href=""><base href="https://outside.example/">' 
                b'<a href="shindan.html">internal</a>')
        self.assertEqual(count_alias_links(src, html)["/shindan.html"], 1)

    def test_invalid_document_base_is_unscanned_not_zero_links(self):
        src = BASE + "/"
        opener = FakeOpener({
            SITEMAP_URL: FakeResponse(SITEMAP_URL, sitemap(src), mime="application/xml"),
            src: FakeResponse(src, b'<base href="https://[invalid"><a href="/shindan.html">x</a>'),
        })
        result = scan(opener)
        self.assertEqual(result["verdict"], "PARTIAL_LINK_INVENTORY_NO_CANONICAL_DECISION")
        self.assertEqual(result["scanned_html_pages"], 0)
        self.assertEqual(result["unscanned_count"], 1)
        self.assertEqual(result["unscanned"][0]["reason"], "invalid_document_base_href")
        self.assertEqual(result["targets"]["/shindan.html"]["occurrences"], 0)

    def test_self_links_are_separate_from_other_page_inbound(self):
        # A diagnosis page linking to itself should not inflate inbound
        # navigation from the rest of the site.
        target, other = BASE + "/photo-diagnosis/", BASE + "/guide/"
        opener = FakeOpener({
            SITEMAP_URL: FakeResponse(SITEMAP_URL, sitemap(target, other), mime="application/xml"),
            target: FakeResponse(target, b'<a href="/photo-diagnosis/">self1</a>'
                                b'<a href="/photo-diagnosis/#step">self2</a>'),
            other: FakeResponse(other, b'<a href="/photo-diagnosis/">from another page</a>'
                              b'<a href="/photo-diagnosis/?ref=guide">from guide CTA</a>'),
        })
        result = scan(opener)
        rec = result["targets"]["/photo-diagnosis/"]
        self.assertEqual(rec["occurrences"], 4)
        self.assertEqual(rec["self_link_occurrences"], 2)
        self.assertEqual(rec["inbound_from_other_pages"], 2)
        self.assertEqual(rec["inbound_referring_pages"], [{"url": other, "count": 2}])
        self.assertEqual(len(rec["referring_pages"]), 2)
        self.assertEqual(result["targets"]["/shindan.html"]["inbound_from_other_pages"], 0)
        self.assertEqual(result["verdict"], "COMPLETE_SITEMAP_HTML_INVENTORY_NO_CANONICAL_DECISION")
        self.assertFalse(result["external_backlinks_checked"])

    def test_redirect_is_not_followed_or_claimed_to_be_a_backlink_free_page(self):
        alias = BASE + "/shindan.html"
        opener = FakeOpener({
            SITEMAP_URL: FakeResponse(SITEMAP_URL, sitemap(alias), mime="application/xml"),
            alias: FakeResponse(alias, status=301),
        })
        result = scan(opener)
        self.assertEqual(result["verdict"], "PARTIAL_LINK_INVENTORY_NO_CANONICAL_DECISION")
        self.assertEqual(result["unscanned_count"], 1)
        self.assertEqual(result["redirected_or_non200_pages"], 1)
        self.assertEqual(opener.calls, [(SITEMAP_URL, "GET"), (alias, "GET")])

    def test_external_sitemap_url_prevents_any_crawl(self):
        good = BASE + "/good"
        opener = FakeOpener({
            SITEMAP_URL: FakeResponse(SITEMAP_URL, sitemap(good, "https://evil.example/"),
                                      mime="application/xml"),
        })
        result = scan(opener)
        self.assertEqual(result["verdict"], "UNVERIFIED_SITEMAP_SCOPE")
        self.assertEqual(len(opener.calls), 1)

    def test_network_failure_is_unknown_not_zero(self):
        opener = FakeOpener({SITEMAP_URL: URLError("DNS unavailable")})
        result = scan(opener)
        self.assertEqual(result["verdict"], "UNVERIFIED_SITEMAP_URLERROR")
        self.assertNotIn("scanned_html_pages", result)

    def test_html_wrong_mime_is_unscanned_not_a_zero_link_proof(self):
        a = BASE + "/a"
        opener = FakeOpener({
            SITEMAP_URL: FakeResponse(SITEMAP_URL, sitemap(a), mime="application/xml"),
            a: FakeResponse(a, b'<a href="/shindan.html">old</a>', mime="application/xml"),
        })
        result = scan(opener)
        self.assertEqual(result["verdict"], "PARTIAL_LINK_INVENTORY_NO_CANONICAL_DECISION")
        self.assertEqual(result["unscanned"][0]["reason"], "unexpected_mime")

    def test_unrelated_schemes_and_domains_never_count(self):
        source = BASE + "/a/"
        body = (b'<a href="javascript:alert(1)"></a>'
                b'<a href="mailto:person@example.com"></a>'
                b'<a href="https://syscom-sustaina-shield.com.evil.example/shindan.html"></a>'
                b'<a href="https://user@syscom-sustaina-shield.com/shindan.html"></a>')
        counts = count_alias_links(source, body)
        self.assertEqual(counts["/shindan.html"], 0)


if __name__ == "__main__":
    unittest.main()
