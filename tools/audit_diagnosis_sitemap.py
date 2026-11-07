#!/usr/bin/env python3
"""GET-only sitemap check for the observed photo-diagnosis redirect alias.

This is an inventory signal, NOT a canonical recommendation. Never rewrite
sitemaps, create redirects, submit Search Console URLs or follow redirects.
If sitemap.xml is an index rather than a urlset, report UNKNOWN (not absent).
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener
from xml.etree import ElementTree

BASE = "https://syscom-sustaina-shield.com"
SITEMAP_URL = BASE + "/sitemap.xml"
ALIAS_URL = BASE + "/shindan.html"
DESTINATION_URL = BASE + "/photo-diagnosis/"
MAX_XML_BYTES = 2_000_000


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def probe(opener=None):
    """Inspect a fixed, allowlisted sitemap URL; no external URLs are fetched."""
    opener = opener or build_opener(NoRedirect)
    req = Request(SITEMAP_URL, headers={
        "Cache-Control": "no-cache", "Accept-Encoding": "identity",
        "User-Agent": "SustainaShield-SitemapAliasReadOnly/1.0",
    }, method="GET")
    result = {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "audit": "GET_only_no_redirect_following",
        "url": SITEMAP_URL,
        "alias": ALIAS_URL,
        "destination": DESTINATION_URL,
        "canonical_policy": "HOLD_external_backlinks_and_Search_Console_not_checked",
        "sitemap_modified": False,
        "search_console_submission": False,
    }
    try:
        try:
            response = opener.open(req, timeout=20)
        except HTTPError as error:
            response = error  # e.g. 301: preserve status, never follow
        with response:
            status = response.status if hasattr(response, "status") else response.code
            actual_url = response.geturl()
            result["http"] = status
            result["exact_url"] = actual_url == SITEMAP_URL
            if status != 200 or actual_url != SITEMAP_URL:
                result["verdict"] = "UNVERIFIED_SITEMAP_HTTP"
                return result
            mime = (response.headers.get("Content-Type") or "").split(";", 1)[0].strip().lower()
            result["content_type"] = mime
            if mime not in ("application/xml", "text/xml", "application/rss+xml", "text/plain"):
                result["verdict"] = "UNVERIFIED_SITEMAP_MIME"
                return result
            body = response.read(MAX_XML_BYTES + 1)
    except (URLError, OSError) as error:
        result["verdict"] = "UNVERIFIED_SITEMAP_NETWORK"
        result["error_type"] = type(error).__name__
        return result

    result["bytes"] = len(body)
    result["sha256"] = hashlib.sha256(body).hexdigest()
    if len(body) > MAX_XML_BYTES:
        result["verdict"] = "UNVERIFIED_SITEMAP_TOO_LARGE"
        return result
    try:
        root = ElementTree.fromstring(body)
    except ElementTree.ParseError:
        result["verdict"] = "UNVERIFIED_SITEMAP_XML_INVALID"
        return result
    kind = root.tag.rsplit("}", 1)[-1]
    result["root_element"] = kind
    if kind != "urlset":
        result["verdict"] = "UNVERIFIED_SITEMAP_INDEX_OR_OTHER_ROOT"
        return result  # Never infer absence from only a sitemap index.

    locs = {(x.text or "").strip() for item in root.findall("{*}url")
            for x in item.findall("{*}loc")}
    result["url_count"] = len(locs)
    result["redirect_alias_listed"] = ALIAS_URL in locs
    result["destination_listed"] = DESTINATION_URL in locs
    result["verdict"] = ("REVIEW_301_ALIAS_LISTED_IN_SITEMAP" if ALIAS_URL in locs
                         else "ALIAS_NOT_LISTED_IN_THIS_URLSET")
    # Only a URL inventory. Cross-check live HTTP, backlinks and GSC separately.
    return result


if __name__ == "__main__":
    print(json.dumps(probe(), ensure_ascii=False, indent=2))
