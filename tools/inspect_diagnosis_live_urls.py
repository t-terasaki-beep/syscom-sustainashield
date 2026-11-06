#!/usr/bin/env python3
"""Read-only, no-redirect HTTP evidence for the two photo-diagnosis aliases.

No POST, sitemap submission, redirects followed, canonical changes, or publication.
This checks public responses only; external backlinks and Search Console are separate.
"""
from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

BASE = "https://syscom-sustaina-shield.com"
PATHS = ("/photo-diagnosis/", "/shindan.html")
MAX_BODY = 1_048_576
OLD_SIZE_REFERENCE = 35904  # Prior 2026-11-03 observation, NOT a current invariant.


class NoRedirect(HTTPRedirectHandler):
    """Never automatically follow an alias redirect (its status is evidence)."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class HeadEvidence(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonical = []
        self.robots = []

    def handle_starttag(self, tag, attrs):
        pairs = dict(attrs)
        if tag == "link" and "canonical" in (pairs.get("rel") or "").lower().split():
            self.canonical.append(pairs.get("href") or "")
        if tag == "meta" and (pairs.get("name") or "").lower() == "robots":
            self.robots.append(pairs.get("content") or "")


def inspect_one(path, opener=None):
    """GET one allowlisted URL without following its 3xx; never modify anything."""
    if path not in PATHS:
        raise ValueError("Unapproved path: no request made")
    url = BASE + path
    req = Request(url, headers={
        "Accept-Encoding": "identity",
        "Cache-Control": "no-cache",
        "User-Agent": "SustainaShield-DiagnosisAliasReadOnly/1.0",
    }, method="GET")
    opener = opener or build_opener(NoRedirect)
    try:
        response = opener.open(req, timeout=20)
    except HTTPError as err:
        # A 301/302 is intentionally preserved, not followed.
        response = err
    except (URLError, OSError) as err:
        return {"url": url, "status": None, "error": str(err),
                "observation": "unavailable_not_zero", "redirect_followed": False}

    with response:
        status = response.status if hasattr(response, "status") else response.code
        headers = response.headers
        result = {
            "url": url, "status": status, "final_url": response.geturl(),
            "redirect_followed": False, "location": headers.get("Location"),
            "etag": headers.get("ETag"), "content_type": headers.get("Content-Type"),
            "x_robots_tag": headers.get("X-Robots-Tag"),
            "http_link_header": headers.get("Link"),
        }
        if status != 200:
            result["body_examined"] = False
            return result
        body = response.read(MAX_BODY + 1)
    result["body_examined"] = True
    result["bytes"] = len(body)
    result["truncated"] = len(body) > MAX_BODY
    if result["truncated"]:
        result["error"] = "HTML over inspection size limit; do not infer canonical"
        return result
    result["sha256"] = hashlib.sha256(body).hexdigest()
    result["matches_2026_11_03_size"] = len(body) == OLD_SIZE_REFERENCE
    mime = (result["content_type"] or "").split(";", 1)[0].strip().lower()
    if mime not in ("text/html", "application/xhtml+xml"):
        result["error"] = "Not an HTML content type"
        return result
    parser = HeadEvidence()
    parser.feed(body.decode("utf-8", errors="replace"))
    result["canonical_links"] = parser.canonical
    result["meta_robots"] = parser.robots
    return result


def snapshot(opener=None):
    records = [inspect_one(path, opener) for path in PATHS]
    same_body = (
        all(r.get("status") == 200 and not r.get("truncated")
            and "sha256" in r for r in records)
        and records[0]["sha256"] == records[1]["sha256"]
    )
    return {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "audit_type": "live_http_get_only_no_redirects",
        "baseline_reference_date": "2026-11-03",
        "same_body_sha256_if_both_200": same_body,
        "external_backlinks_checked": False,
        "search_console_checked": False,
        "canonical_decision": "HOLD_pending_external_links_and_search_console",
        "routes": records,
    }


if __name__ == "__main__":
    print(json.dumps(snapshot(), ensure_ascii=False, indent=2))
