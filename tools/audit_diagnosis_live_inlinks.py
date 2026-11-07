#!/usr/bin/env python3
"""GET-only production internal-link inventory for P1 photo-diagnosis aliases.

Only same-origin URLs explicitly listed in the current sitemap are fetched.
No redirect following, external backlinks, Search Console, canonical edits,
sitemap writes, or publication. Partial scans are never presented as zero links.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from xml.etree import ElementTree

BASE = "https://syscom-sustaina-shield.com"
SITEMAP_URL = BASE + "/sitemap.xml"
TARGETS = ("/photo-diagnosis/", "/shindan.html")
MAX_SITEMAP_BYTES = 2_000_000
MAX_HTML_BYTES = 1_500_000
MAX_PAGES = 250


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            href = dict(attrs).get("href")
            if href:
                self.hrefs.append(href)


def same_origin(url):
    try:
        parsed = urlsplit(url)
        return (parsed.scheme == "https" and parsed.hostname == "syscom-sustaina-shield.com"
                and parsed.port is None and not parsed.username and not parsed.password
                and not parsed.query and not parsed.fragment)
    except ValueError:
        return False


def count_alias_links(source_url, body):
    """Count anchor targets only; do not fetch hrefs or count canonical tags."""
    parser = Anchors()
    parser.feed(body.decode("utf-8", errors="replace"))
    counts = {p: 0 for p in TARGETS}
    for href in parser.hrefs:
        try:
            target = urljoin(source_url, href)
            parts = urlsplit(target)
            # Anchor queries/fragments are still links to the same document.
            clean = parts._replace(query="", fragment="").geturl()
            if same_origin(clean) and parts.path in counts:
                counts[parts.path] += 1
        except ValueError:
            continue
    return counts


def fetch(opener, url, limit, accepted_mimes):
    """Return (status, body, reason); never follow a 3xx or expose response HTML."""
    req = Request(url, headers={"Cache-Control": "no-cache", "Accept-Encoding": "identity",
                                "User-Agent": "SustainaShield-P1-InternalLinks/1.0"}, method="GET")
    try:
        try:
            response = opener.open(req, timeout=15)
        except HTTPError as err:
            response = err
        with response:
            status = response.status if hasattr(response, "status") else response.code
            if response.geturl() != url:
                return status, None, "unexpected_final_url"
            if status != 200:
                return status, None, "non_200_not_followed"
            mime = (response.headers.get("Content-Type") or "").split(";", 1)[0].strip().lower()
            if mime not in accepted_mimes:
                return status, None, "unexpected_mime"
            body = response.read(limit + 1)
            if len(body) > limit:
                return status, None, "over_byte_limit"
            return status, body, None
    except (URLError, OSError) as err:
        return None, None, type(err).__name__


def scan(opener=None):
    opener = opener or build_opener(NoRedirect)
    report = {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "current_sitemap_same_origin_HTML_anchor_links_ONLY",
        "external_backlinks_checked": False, "search_console_checked": False,
        "canonical_policy": "HOLD_no_redirect_or_canonical_change",
        "production_modified": False, "http_method": "GET",
        "targets": {p: {"occurrences": 0, "referring_pages": []} for p in TARGETS},
        "unscanned": [],
    }
    status, raw, problem = fetch(opener, SITEMAP_URL, MAX_SITEMAP_BYTES, ("application/xml", "text/xml", "text/plain"))
    report["sitemap_http"] = status
    if problem:
        report["verdict"] = "UNVERIFIED_SITEMAP_" + problem.upper()
        return report
    try:
        root = ElementTree.fromstring(raw)
    except ElementTree.ParseError:
        report["verdict"] = "UNVERIFIED_INVALID_XML"
        return report
    if root.tag.rsplit("}", 1)[-1] != "urlset":
        report["verdict"] = "UNVERIFIED_NOT_URLSET"
        return report
    listed = sorted(set((loc.text or "").strip() for loc in root.findall("{*}url")
                        for loc in loc.findall("{*}loc")))
    report["sitemap_url_count"] = len(listed)
    if len(listed) > MAX_PAGES or not listed or any(not same_origin(u) for u in listed):
        report["verdict"] = "UNVERIFIED_SITEMAP_SCOPE"
        return report
    report["scanned_html_pages"] = 0
    report["redirected_or_non200_pages"] = 0
    for url in listed:
        status, body, problem = fetch(opener, url, MAX_HTML_BYTES, ("text/html", "application/xhtml+xml"))
        if problem:
            report["unscanned"].append({"url": url, "http": status, "reason": problem})
            if problem == "non_200_not_followed":
                report["redirected_or_non200_pages"] += 1
            continue
        report["scanned_html_pages"] += 1
        for path, n in count_alias_links(url, body).items():
            if n:
                report["targets"][path]["occurrences"] += n
                report["targets"][path]["referring_pages"].append({"url": url, "count": n})
    report["unscanned_count"] = len(report["unscanned"])
    report["verdict"] = ("PARTIAL_LINK_INVENTORY_NO_CANONICAL_DECISION"
                         if report["unscanned"] else "COMPLETE_SITEMAP_HTML_INVENTORY_NO_CANONICAL_DECISION")
    # Both verdicts remain insufficient to choose a canonical: external links
    # and Search Console have not been verified.
    return report


if __name__ == "__main__":
    print(json.dumps(scan(), ensure_ascii=False, indent=2))
