"""Unit tests for P1 read-only sitemap-wide HTML link extraction; no network."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_photo_diagnosis_live_links import LinkReader, normalize_target, sitemap_items


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

    def test_reject_empty_sitemap(self):
        with self.assertRaises(ValueError):
            sitemap_items(b'<urlset></urlset>')


if __name__ == "__main__":
    unittest.main()
