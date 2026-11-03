#!/usr/bin/env python3
"""Read-only, no-redirect production evidence capture for two photo-diagnosis URLs.

This tool deliberately has no write, deploy, authentication, or canonical-change path.
It reports *observations*, not SEO decisions. Run from the approved inspection host.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from datetime import datetime, timezone
from urllib import error, request

URLS = (
    "https://syscom-sustaina-shield.com/photo-diagnosis/",
    "https://syscom-sustaina-shield.com/shindan.html",
)


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class HeadParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.canonicals = []
        self.robots = []
        self._title = False
        self.title = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag.lower() == "link" and "canonical" in a.get("rel", "").lower().split():
            self.canonicals.append(a.get("href", ""))
        if tag.lower() == "meta" and a.get("name", "").lower() == "robots":
            self.robots.append(a.get("content", ""))
        if tag.lower() == "title":
            self._title = True

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self._title = False

    def handle_data(self, data):
        if self._title:
            self.title += data


def inspect(opener, url, timeout=10.0, max_bytes=1000000):
    req = request.Request(url, method="GET", headers={
        "User-Agent": "SustainashieldReadOnlyURLAudit/1.0",
        "Accept-Encoding": "identity",
    })
    try:
        response = opener.open(req, timeout=timeout)
    except error.HTTPError as exc:
        # With redirects disabled, urllib surfaces 3xx as HTTPError.
        response = exc
    except (error.URLError, TimeoutError, OSError) as exc:
        return {"url": url, "error": type(exc).__name__ + ": " + str(exc)}

    with response:
        status = getattr(response, "status", None) or response.getcode()
        h = response.headers
        entry = {
            "url": url,
            "http_status": status,
            "location": h.get("Location"),
            "etag": h.get("ETag"),
            "content_length_header": h.get("Content-Length"),
            "x_robots_tag": h.get("X-Robots-Tag"),
            "redirect_followed": False,
        }
        # Don't digest a redirect's error document: it is not the target HTML.
        if status != 200:
            return entry
        data = response.read(max_bytes + 1)
        if len(data) > max_bytes:
            return {**entry, "error": "HTML exceeds maximum read size"}
        entry["body_bytes"] = len(data)
        entry["sha256"] = hashlib.sha256(data).hexdigest()
        html = data.decode("utf-8", errors="replace")
        p = HeadParser()
        p.feed(html)
        entry["title"] = p.title.strip()
        entry["canonical_links"] = p.canonicals
        entry["meta_robots"] = p.robots
        entry["ss_analytics_script_count"] = html.count('/assets/ss-analytics.js')
        return entry


def collect(opener, timeout=10.0, max_bytes=1000000):
    rows = [inspect(opener, u, timeout=timeout, max_bytes=max_bytes) for u in URLS]
    both_200 = all(r.get("http_status") == 200 and "sha256" in r for r in rows)
    return {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "P1 observation only; no canonical or 301 decision",
        "urls": rows,
        "same_body_sha256_if_both_200": (
            rows[0]["sha256"] == rows[1]["sha256"] if both_200 else None
        ),
        "status": "observed_both_200" if both_200 else "incomplete_or_redirected",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--max-bytes", type=int, default=1000000)
    args = parser.parse_args()
    if not (0 < args.timeout <= 60 and 1000 <= args.max_bytes <= 5000000):
        parser.error("timeout and max-bytes outside safe bounds")
    opener = request.build_opener(NoRedirect())
    print(json.dumps(collect(opener, args.timeout, args.max_bytes),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
