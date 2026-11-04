"""Unit tests for P1 read-only sitemap-wide HTML link extraction; no network."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_photo_diagnosis_live_links import LinkReader, normalize_target, sitemap_items, inspect_page, summarize_sitemap_seo
from unittest.mock import patch


class TestP1LiveLinkAudit(unittest.TestCase):
    def test_legacy_relative(self):
        self.assertEqual(normalize_target("https://syscom-sustaina-shield.com/residential/",
                                          "../shindan.html?utm=a#start"), "/shindan.html")

    def test_new_absolute_and_index(self):
        self.assertEqual(normalize_target("https://syscom-sustaina-shield.com/",
                                          "/photo-diagnosis/index.html"), "/photo-diagnosis/")
        self.assertEqual(normalize_target("https://syscom-sustaina-shield.com/",
                                          "/photo-diagnosis/?utm_source=menu"), "/photo-diagnosis/")

    def test_no_external_lookalike(self):
        self.assertIsNone(normalize_target("https://syscom-sustaina-shield.com/",
                                           "https://syscom-sustaina-shield.com.evil.tld/shindan.html"))
        self.assertIsNone(normalize_target("https://syscom-sustaina-shield.com/",
                                           "http://syscom-sustaina-shield.com/shindan.html"))

    def test_only_anchor_links(self):
        parser = LinkReader()
        parser.feed('<a href="/shindan.html">old</a><A HREF="/photo-diagnosis/">new</A>'
                    '<script>"/shindan.html"</script><link href="/shindan.html">')
        self.assertEqual(parser.hrefs, ["/shindan.html", "/photo-diagnosis/"])

    def test_fragment_only_not_counted_as_inbound_link(self):
        self.assertIsNone(normalize_target("https://syscom-sustaina-shield.com/photo-diagnosis/", "#main"))
        self.assertIsNone(normalize_target("https://syscom-sustaina-shield.com/photo-diagnosis/", ""))

    def test_known_redirect_301_counts_as_verified_route(self):
        with patch("audit_photo_diagnosis_live_links.fetch", return_value=(301, "text/html", b"", "https://syscom-sustaina-shield.com/photo-diagnosis/")):
            d = inspect_page("https://syscom-sustaina-shield.com/shindan.html")
        self.assertEqual(d["http"], 301)
        self.assertNotIn("issue", d)

    def test_unknown_redirect_does_not_count_as_healthy(self):
        with patch("audit_photo_diagnosis_live_links.fetch", return_value=(301, "text/html", b"", "https://evil.example/")):
            d = inspect_page("https://syscom-sustaina-shield.com/shindan.html")
        self.assertIn("issue", d)

    def test_sitemap_urlset(self):
        xml = (b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
               b'<url><loc>https://syscom-sustaina-shield.com/</loc></url></urlset>')
        self.assertEqual(sitemap_items(xml), ("urlset", ["https://syscom-sustaina-shield.com/"]))

    def test_sitemap_index(self):
        xml = (b'<sitemapindex><sitemap>'
               b'<loc>https://syscom-sustaina-shield.com/sitemap-pages.xml</loc>'
               b'</sitemap></sitemapindex>')
        self.assertEqual(sitemap_items(xml)[0], "sitemapindex")

    def test_reject_external_sitemap_url(self):
        with self.assertRaises(ValueError):
            sitemap_items(b'<urlset><url><loc>https://external.example/</loc></url></urlset>')

    def test_existing_301_sitemap_signal_is_explicit_and_read_only(self):
        root = "https://syscom-sustaina-shield.com"
        legacy, dest = root + "/shindan.html", root + "/photo-diagnosis/"
        report = summarize_sitemap_seo(
            [legacy, dest],
            [{"url": legacy, "http": 301, "redirect_to": dest},
             {"url": dest, "http": 200}])
        self.assertEqual(report["status"], "EXISTING_301_URL_INCLUDED_IN_SITEMAP")
        self.assertTrue(report["legacy_listed"])
        self.assertTrue(report["destination_listed"])
        self.assertTrue(report["observed_existing_301"])
        self.assertIn("HOLD_NO_SITEMAP", report["decision"])

    def test_unverified_sitemap_route_is_not_called_a_known_redirect(self):
        root = "https://syscom-sustaina-shield.com"
        legacy = root + "/shindan.html"
        report = summarize_sitemap_seo(
            [legacy], [{"url": legacy, "issue": "TimeoutError"}])
        self.assertEqual(report["status"], "LEGACY_SITEMAP_URL_ROUTE_UNVERIFIED")
        self.assertFalse(report["observed_existing_301"])

    def test_missing_legacy_sitemap_does_not_imply_external_links_absent(self):
        root = "https://syscom-sustaina-shield.com"
        report = summarize_sitemap_seo([root + "/photo-diagnosis/"], [])
        self.assertEqual(report["status"], "LEGACY_URL_NOT_LISTED_IN_SITEMAP")
        self.assertIn("GSC_AND_BACKLINKS", report["decision"])

    def test_reject_empty_sitemap(self):
        with self.assertRaises(ValueError):
            sitemap_items(b'<urlset></urlset>')


if __name__ == "__main__":
    unittest.main()
