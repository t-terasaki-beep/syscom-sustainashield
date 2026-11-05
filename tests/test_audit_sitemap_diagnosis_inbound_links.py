"""Offline-only tests: no site traffic, credentials or publication."""
import importlib.util
from pathlib import Path
from email.message import Message
import unittest

P = Path(__file__).resolve().parents[1] / "tools" / "audit_sitemap_diagnosis_inbound_links.py"
spec = importlib.util.spec_from_file_location("sitemap_audit", P)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Response:
    def __init__(self, payload, status=200, location=None):
        self.payload = payload
        self.status = status
        self.headers = Message()
        if location is not None:
            self.headers["Location"] = location

    def __enter__(self): return self
    def __exit__(self, *_): pass
    def read(self, size): return self.payload[:size]


class FakeOpener:
    def __init__(self, bodies):
        self.bodies = bodies
        self.requested = []

    def open(self, req, timeout):
        self.requested.append((req.full_url, req.get_method(), timeout))
        return self.bodies[req.full_url]


def urlset(*urls):
    return ('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
            ''.join("<url><loc>" + x + "</loc></url>" for x in urls) +
            "</urlset>").encode()


def index(*urls):
    return ('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
            ''.join("<sitemap><loc>" + x + "</loc></sitemap>" for x in urls) +
            "</sitemapindex>").encode()


class SitemapAuditTests(unittest.TestCase):
    def test_urlset_reads_and_deduplicates_same_host(self):
        root = m.sampler.SITE
        f = FakeOpener({root+"/sitemap.xml": Response(urlset(
            root+"/", root+"/residential/", root+"/"))})
        paths, sources = m.enumerate_paths(f)
        self.assertEqual(paths, ["/", "/residential/"])
        self.assertEqual(sources, ["/sitemap.xml"])
        self.assertEqual(f.requested, [(root+"/sitemap.xml", "GET", 15)])

    def test_child_sitemap_index_read_without_external_requests(self):
        root = m.sampler.SITE
        f = FakeOpener({
            root+"/sitemap.xml": Response(index(root+"/a.xml", root+"/b.xml")),
            root+"/a.xml": Response(urlset(root+"/", root+"/faq.html")),
            root+"/b.xml": Response(urlset(root+"/faq.html", root+"/solar/"))
        })
        paths, sources = m.enumerate_paths(f)
        self.assertEqual(paths, ["/", "/faq.html", "/solar/"])
        self.assertEqual(len(sources), 3)

    def test_rejects_offsite_query_and_untrusted_scheme(self):
        for address in ("https://elsewhere.test/page", "http://syscom-sustaina-shield.com/",
                        m.sampler.SITE+"/?foo=1", "https://user@syscom-sustaina-shield.com/"):
            with self.subTest(address=address):
                with self.assertRaises(m.SitemapAuditError):
                    m.accepted_url(address)

    def test_rejects_oversize_and_invalid_xml_and_empty_urls(self):
        with self.assertRaises(m.SitemapAuditError):
            m.parse_sitemap(b"<html></html>")
        with self.assertRaises(m.SitemapAuditError):
            m.parse_sitemap(b"<urlset")
        with self.assertRaises(m.SitemapAuditError):
            m.parse_sitemap(urlset())
        f = FakeOpener({m.sampler.SITE+"/sitemap.xml":
                        Response(b"x" * (m.MAX_SITEMAP_BYTES+1))})
        with self.assertRaises(m.SitemapAuditError):
            m.enumerate_paths(f)

    def test_sitewide_totals_and_incomplete_are_never_silent(self):
        root = m.sampler.SITE
        payloads = {
            root+"/": Response(b'<a href="/shindan.html">old</a>'),
            root+"/faq.html": Response(b'<a href="/photo-diagnosis/">new</a>'),
        }
        report = m.collect_sitewide(lambda: FakeOpener(payloads),
                                    ["/", "/faq.html"], ["/sitemap.xml"])
        self.assertTrue(report["complete"])
        self.assertEqual(report["sitemap_page_count"], 2)
        self.assertEqual(report["anchor_totals"], {"/shindan.html": 1,
                                                  "/photo-diagnosis/": 1})
        self.assertEqual(report["pages_with_old_url"], ["/"])
        self.assertEqual(report["pages_with_new_url"], ["/faq.html"])
        self.assertEqual(report["decision"], "NO_CANONICAL_OR_REDIRECT_CHANGE")
        payloads[root+"/faq.html"] = Response(b"error", status=404)
        incomplete = m.collect_sitewide(lambda: FakeOpener(payloads),
                                        ["/", "/faq.html"], ["/sitemap.xml"])
        self.assertFalse(incomplete["complete"])
        self.assertEqual(incomplete["http_200_count"], 1)

    def test_known_legacy_301_to_current_200_is_classified_separately(self):
        root = m.sampler.SITE
        payloads = {
            root + "/shindan.html": Response(b"", status=301,
                                            location=root + "/photo-diagnosis/"),
            root + "/photo-diagnosis/": Response(b'<a href="/photo-diagnosis/">new</a>'),
        }
        result = m.collect_sitewide(lambda: FakeOpener(payloads),
                                    ["/shindan.html", "/photo-diagnosis/"], ["/sitemap.xml"])
        self.assertTrue(result["complete"])
        self.assertEqual(result["http_200_count"], 1)
        self.assertEqual(result["verified_legacy_301_count"], 1)
        self.assertTrue(result["sitemap_contains_legacy_redirect_url"])
        self.assertEqual(result["anchor_totals"], {"/shindan.html": 0,
                                                   "/photo-diagnosis/": 1})

    def test_wrong_legacy_redirect_or_missing_destination_remains_incomplete(self):
        root = m.sampler.SITE
        for location, current_status in ((root + "/wrong/", 200),
                                         (root + "/photo-diagnosis/", 404)):
            with self.subTest(location=location, current_status=current_status):
                payloads = {
                    root + "/shindan.html": Response(b"", status=301, location=location),
                    root + "/photo-diagnosis/": Response(b"", status=current_status),
                }
                report = m.collect_sitewide(lambda: FakeOpener(payloads),
                                            ["/shindan.html", "/photo-diagnosis/"], ["/sitemap.xml"])
                self.assertFalse(report["complete"])
                self.assertEqual(report["verified_legacy_301_count"], 0)


if __name__ == "__main__":
    unittest.main()
