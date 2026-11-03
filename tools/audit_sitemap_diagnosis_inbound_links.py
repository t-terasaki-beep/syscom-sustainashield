#!/usr/bin/env python3
"""Read-only, bounded sitemap-wide audit of live photo-diagnosis inbound anchors.

No redirects, production writes, login, API tokens, SEO changes or submissions.
Only URLs verified inside the production sitemap on the same HTTPS host are read.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys
from urllib import request
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

SAMPLER = Path(__file__).with_name("audit_live_diagnosis_inbound_links.py")
_spec = importlib.util.spec_from_file_location("diagnosis_sampler", SAMPLER)
sampler = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sampler)

MAX_SITEMAPS = 6
MAX_URLS = 250
MAX_SITEMAP_BYTES = 1_500_000
WORKERS = 5


class SitemapAuditError(ValueError):
    pass


def accepted_url(value):
    """No cross-domain, non-HTTPS, query, fragment or credentialed requests."""
    parsed = urlsplit(value.strip())
    site = urlsplit(sampler.SITE)
    if (parsed.scheme != "https" or parsed.netloc.lower() != site.netloc
            or parsed.username is not None or parsed.password is not None
            or parsed.query or parsed.fragment or not parsed.path.startswith("/")):
        raise SitemapAuditError("Unexpected or off-site sitemap URL: " + value[:120])
    return parsed.path


def parse_sitemap(xml_bytes):
    """Return (kind, links); reject malformed XML, unknown document types and empties."""
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise SitemapAuditError("Malformed sitemap XML") from exc
    kind = root.tag.rsplit("}", 1)[-1]
    if kind not in ("urlset", "sitemapindex"):
        raise SitemapAuditError("Unexpected sitemap XML root: " + kind)
    item = "url" if kind == "urlset" else "sitemap"
    links = []
    for node in root:
        if node.tag.rsplit("}", 1)[-1] != item:
            continue
        for child in node:
            if child.tag.rsplit("}", 1)[-1] == "loc" and child.text:
                links.append(child.text.strip())
                break
    if not links:
        raise SitemapAuditError("Sitemap contains no valid loc elements")
    return kind, links


def read_sitemap(opener, path):
    req = request.Request(sampler.SITE + path, method="GET", headers={
        "Accept-Encoding": "identity",
        "User-Agent": "SustainaShield-LinkAudit/1.1",
    })
    with opener.open(req, timeout=15) as response:
        if response.status != 200:
            raise SitemapAuditError(f"Non-200 sitemap response: {response.status}")
        data = response.read(MAX_SITEMAP_BYTES + 1)
        if len(data) > MAX_SITEMAP_BYTES:
            raise SitemapAuditError("Sitemap exceeds byte limit")
    return parse_sitemap(data)


def enumerate_paths(opener, initial_path="/sitemap.xml"):
    """Fail closed on path drift, external URLs, oversized sitemap or nested indices."""
    queue = [initial_path]
    visited = set()
    pages = []
    seen_pages = set()
    while queue:
        path = queue.pop(0)
        if path in visited:
            continue
        if len(visited) >= MAX_SITEMAPS:
            raise SitemapAuditError("Sitemap count exceeds cap")
        visited.add(path)
        kind, urls = read_sitemap(opener, path)
        for value in urls:
            target = accepted_url(value)
            if kind == "sitemapindex":
                if not target.endswith(".xml"):
                    raise SitemapAuditError("Unexpected child sitemap extension")
                if target not in visited and target not in queue:
                    queue.append(target)
                if len(queue) + len(visited) > MAX_SITEMAPS:
                    raise SitemapAuditError("Sitemap index exceeds cap")
            elif target not in seen_pages:
                pages.append(target)
                seen_pages.add(target)
                if len(pages) > MAX_URLS:
                    raise SitemapAuditError("Sitemap URL count exceeds cap")
    if not pages:
        raise SitemapAuditError("No page URLs enumerated; cannot claim zero links")
    return pages, sorted(visited)


def collect_sitewide(opener_factory, paths, sitemap_files):
    # Per-thread opener avoids sharing mutable opener state across requests.
    def inspect_path(path):
        return sampler.inspect(opener_factory(), path)

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        pages = list(pool.map(inspect_path, paths))
    totals = {target: sum(row.get("tracked_anchor_counts", {}).get(target, 0)
                          for row in pages) for target in sampler.TRACKED}
    complete = all(row.get("http_status") == 200 and "error" not in row
                   for row in pages)
    return {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Sitemap-listed LIVE HTML only; <a href> only (no JS links or external backlinks)",
        "sitemap_files": sitemap_files,
        "sitemap_page_count": len(paths),
        "http_200_count": sum(row.get("http_status") == 200 for row in pages),
        "complete": complete,
        "anchor_totals": totals,
        "pages_with_old_url": [r["page"] for r in pages
                              if r.get("tracked_anchor_counts", {}).get("/shindan.html", 0)],
        "pages_with_new_url": [r["page"] for r in pages
                              if r.get("tracked_anchor_counts", {}).get("/photo-diagnosis/", 0)],
        "pages": pages,
        "redirect_followed": False,
        "decision": "NO_CANONICAL_OR_REDIRECT_CHANGE",
    }


def main():
    sitemap_opener = request.build_opener(sampler.NoRedirect())
    try:
        paths, files = enumerate_paths(sitemap_opener)
        report = collect_sitewide(
            lambda: request.build_opener(sampler.NoRedirect()), paths, files)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if not report["complete"]:
            print("WARNING: not all sitemap pages returned HTTP200; no sitewide zero claim",
                  file=sys.stderr)
            return 2
        return 0
    except (SitemapAuditError, OSError, ValueError) as exc:
        print(json.dumps({"complete": False, "error": str(exc),
                          "decision": "NO_CANONICAL_OR_REDIRECT_CHANGE"},
                         ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
