#!/usr/bin/env python3
"""Read-only sample of LIVE internal links to the two photo-diagnosis URLs.

Ten fixed, high-level production pages; no crawl, redirect follow, auth, writes,
SEO changes, or external submissions. HTML anchors only (not JS-generated links).
"""
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import sys
from urllib import request, error
from urllib.parse import urljoin, urlsplit

SITE = "https://syscom-sustaina-shield.com"
PATHS = (
    "/", "/residential/", "/faq.html", "/company.html", "/contact.html",
    # Five additional verified-in-project routes; this remains a sample, not a crawl.
    "/bcp/", "/solar/", "/aliphatic-polyurea-chiba/",
    "/residential/chiba-blackout/", "/column/shoene2024-data-leak-alert/",
)
TRACKED = ("/shindan.html", "/photo-diagnosis/")
MAX_BYTES = 750_000


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class AnchorHrefParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            for key, value in attrs:
                if key.lower() == "href" and value:
                    self.hrefs.append(value)
                    break


def classify_href(href, source_url):
    """Only classify actual anchors to precisely the two local paths."""
    try:
        u = urlsplit(urljoin(source_url, href.strip()))
        if u.scheme != "https" or u.netloc.lower() != urlsplit(SITE).netloc:
            return None
        return u.path if u.path in TRACKED else None
    except ValueError:
        return None


def inspect(opener, path):
    url = SITE + path
    req = request.Request(url, method="GET", headers={
        "Accept-Encoding": "identity", "User-Agent": "SustainaShield-LinkAudit/1.0",
    })
    try:
        resp = opener.open(req, timeout=10)
    except error.HTTPError as exc:
        resp = exc  # non-200 or redirect: record and do not follow
    except (error.URLError, TimeoutError, OSError) as exc:
        return {"page": path, "error": type(exc).__name__}
    with resp:
        status = getattr(resp, "status", None) or resp.getcode()
        etag = resp.headers.get("ETag")
        record = {"page": path, "http_status": status, "etag": etag}
        if status != 200:
            return record
        body = resp.read(MAX_BYTES + 1)
        if len(body) > MAX_BYTES:
            return {**record, "error": "HTML_EXCEEDS_READ_CAP"}
        parser = AnchorHrefParser()
        parser.feed(body.decode("utf-8", errors="replace"))
        counts = {p: 0 for p in TRACKED}
        for href in parser.hrefs:
            target = classify_href(href, url)
            if target:
                counts[target] += 1
        record["tracked_anchor_counts"] = counts
        record["total_anchors"] = len(parser.hrefs)
        return record


def collect(opener):
    pages = [inspect(opener, p) for p in PATHS]
    totals = {p: sum(x.get("tracked_anchor_counts", {}).get(p, 0) for x in pages)
              for p in TRACKED}
    return {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": f"{len(PATHS)} sampled LIVE HTML pages, only <a href>; no sitewide claim",
        "redirect_followed": False,
        "pages": pages,
        "anchor_totals": totals,
        "complete": all(x.get("http_status") == 200 and "error" not in x for x in pages),
        "decision": "NO_CANONICAL_OR_REDIRECT_CHANGE",
    }


def main():
    report = collect(request.build_opener(NoRedirect()))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["complete"]:
        print("Some sampled pages not observed; do not extrapolate", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
