#!/usr/bin/env python3
"""Read-only sitemap-wide production HTML link audit for photo-diagnosis URLs.

Evidence only: do not edit URLs, redirects, canonical, analytics or live pages.
This is distinct from the repository-only link audit. No Google Search Console
or external backlink data is claimed.
"""
from __future__ import annotations

import concurrent.futures
import json
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.error import HTTPError
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from xml.etree import ElementTree

ORIGIN = "https://syscom-sustaina-shield.com"
SITEMAP = ORIGIN + "/sitemap.xml"
TARGETS = ("/shindan.html", "/photo-diagnosis/")
MAX_URLS = 250
MAX_BODY = 1024 * 1024
HEADERS = {
    "Accept-Encoding": "identity",
    "Cache-Control": "no-cache",
    "User-Agent": "SustainaShield-P1-SitemapEvidence/1.0",
}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class LinkReader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            self.hrefs += [value for key, value in attrs
                           if key.lower() == "href" and value]


def normalize_target(source_url: str, href: str) -> str | None:
    raw_href = href.strip()
    # Fragment-only and empty hrefs are same-page controls, not inbound navigation.
    if not raw_href or raw_href.startswith("#"):
        return None
    resolved = urlsplit(urljoin(source_url, raw_href))
    if resolved.scheme != "https" or resolved.netloc.lower() != "syscom-sustaina-shield.com":
        return None
    path = unquote(resolved.path)
    if path == "/photo-diagnosis/index.html":
        path = "/photo-diagnosis/"
    return path if path in TARGETS else None


def sitemap_items(xml: bytes) -> tuple[str, list[str]]:
    root = ElementTree.fromstring(xml)
    kind = root.tag.rsplit("}", 1)[-1]
    if kind not in ("urlset", "sitemapindex"):
        raise ValueError("Unexpected sitemap XML root")
    values = []
    for item in root:
        expected = "url" if kind == "urlset" else "sitemap"
        if item.tag.rsplit("}", 1)[-1] != expected:
            continue
        loc = next((x.text or "" for x in item
                    if x.tag.rsplit("}", 1)[-1] == "loc"), "").strip()
        parsed = urlsplit(loc)
        if (parsed.scheme != "https" or
                parsed.netloc.lower() != "syscom-sustaina-shield.com" or
                parsed.query or parsed.fragment):
            raise ValueError("Sitemap contains unexpected or non-site URL")
        values.append(loc)
    if not values:
        raise ValueError("Sitemap has no valid entries")
    return kind, values


def fetch(url: str, *, max_bytes: int = MAX_BODY) -> tuple[int, str, bytes, str | None]:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc.lower() != "syscom-sustaina-shield.com":
        raise ValueError("Out-of-scope host")
    req = Request(url, headers=HEADERS)
    opener = build_opener(NoRedirect)
    try:
        response = opener.open(req, timeout=12)
    except HTTPError as error:
        response = error  # Do not follow a 301 and mistake it for a live HTML file.
    with response:
        code = response.status
        content_type = response.headers.get("Content-Type", "")
        location = response.headers.get("Location")
        blob = response.read(max_bytes + 1)
    if len(blob) > max_bytes:
        raise ValueError("Response exceeded size cap")
    return code, content_type, blob, location


def get_sitemap_urls(start: str = SITEMAP) -> list[str]:
    pending = [(start, 0)]
    checked = set()
    pages = []
    while pending:
        url, depth = pending.pop(0)
        if url in checked or depth > 2:
            raise ValueError("Sitemap duplicate or recursion depth exceeded")
        checked.add(url)
        status, content_type, blob, _location = fetch(url, max_bytes=2 * MAX_BODY)
        if status != 200 or "xml" not in content_type.lower():
            raise ValueError("Sitemap not HTTP200/XML")
        kind, urls = sitemap_items(blob)
        if kind == "sitemapindex":
            pending.extend((x, depth + 1) for x in urls)
        else:
            pages.extend(urls)
        if len(pages) > MAX_URLS or len(pending) > MAX_URLS:
            raise ValueError("Sitemap exceeds safety cap")
    if len(pages) != len(set(pages)):
        raise ValueError("Duplicate URLs in sitemap; review before counting")
    return pages


def inspect_page(url: str) -> dict:
    try:
        status, content_type, blob, location = fetch(url)
        # The sitemap includes the existing legacy 301: preserve it as a
        # verified redirect, not an HTML fetch failure or a newly added rule.
        if (url == ORIGIN + "/shindan.html" and status == 301 and
                location == ORIGIN + "/photo-diagnosis/"):
            return {"url": url, "http": 301, "redirect_to": location}
        if status != 200 or "html" not in content_type.lower():
            return {"url": url, "http": status, "issue": "Not HTTP200 HTML"}
        parser = LinkReader()
        parser.feed(blob.decode("utf-8", errors="replace"))
        links = {target: [] for target in TARGETS}
        for href in parser.hrefs:
            target = normalize_target(url, href)
            if target:
                links[target].append(href)
        return {"url": url, "http": 200, "matches": links}
    except Exception as exc:
        return {"url": url, "issue": type(exc).__name__}



def summarize_sitemap_seo(urls: list[str], results: list[dict]) -> dict:
    """Surface a 301 URL in XML sitemap as a hygiene issue, not an edit request.

    The 301 was already live. Google Search Console and external backlinks must
    be reviewed separately before changing sitemap, redirect, or canonical.
    """
    legacy = ORIGIN + "/shindan.html"
    destination = ORIGIN + "/photo-diagnosis/"
    listed_legacy = legacy in urls
    listed_destination = destination in urls
    old_response = next((row for row in results if row.get("url") == legacy), None)
    already_redirecting = bool(
        old_response and old_response.get("http") == 301
        and old_response.get("redirect_to") == destination
    )
    if listed_legacy and already_redirecting:
        status = "EXISTING_301_URL_INCLUDED_IN_SITEMAP"
    elif listed_legacy:
        status = "LEGACY_SITEMAP_URL_ROUTE_UNVERIFIED"
    else:
        status = "LEGACY_URL_NOT_LISTED_IN_SITEMAP"
    return {
        "status": status,
        "legacy_listed": listed_legacy,
        "destination_listed": listed_destination,
        "observed_existing_301": already_redirecting,
        "decision": "HOLD_NO_SITEMAP_REDIRECT_CANONICAL_CHANGE_UNTIL_GSC_AND_BACKLINKS",
        "scope": "Only sitemap-listed URL status, not Search Console indexing or external backlinks",
    }


def audit() -> dict:
    urls = get_sitemap_urls()
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(inspect_page, urls))
    failures = [{k: v for k, v in item.items() if k != "matches"}
                for item in results if "issue" in item]
    legacy_redirects = [item for item in results if item.get("http") == 301]
    counts = {target: 0 for target in TARGETS}
    sources = {target: [] for target in TARGETS}
    for page in results:
        for target, hrefs in page.get("matches", {}).items():
            if hrefs:
                counts[target] += len(hrefs)
                sources[target].append({"source_url": page["url"], "links": len(hrefs),
                                        "href_examples": hrefs[:3]})
    return {
        "observed_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Sitemap-listed live HTML a[href] only; no JS links, external backlinks or GSC",
        "sitemap_url": SITEMAP,
        "sitemap_urls": len(urls),
        "http200_html_pages": len(results) - len(failures) - len(legacy_redirects),
        "verified_existing_legacy_301": len(legacy_redirects),
        "sitemap_seo_hygiene": summarize_sitemap_seo(urls, results),
        "errors": failures,
        "href_counts": counts,
        "unique_source_page_counts": {target: len(items) for target, items in sources.items()},
        "sources": sources,
        "canonical_or_redirect_changes": 0,
        "complete": not failures,
    }


def main() -> int:
    try:
        result = audit()
    except Exception as error:
        print(json.dumps({"complete": False, "error_type": type(error).__name__,
                          "message": str(error), "production_changes": 0}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["sitemap_seo_hygiene"]["status"] == "EXISTING_301_URL_INCLUDED_IN_SITEMAP":
        print("::warning title=P1 sitemap hygiene::An already-301 URL is in sitemap; review GSC/external links before any change.", file=sys.stderr)
    if not result["complete"]:
        print("::warning title=P1 incomplete::Do not claim a site-wide count.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
