#!/usr/bin/env python3
"""Aggregate photo-diagnosis alias links in GitHub HTML only.

No network requests, redirects, canonical edits, or production changes.
This inventory does not represent a live-site crawl or external backlinks.
"""
import json
import sys
from pathlib import Path
from conversion_audit import audit

ALIASES = ("/photo-diagnosis/", "/shindan.html")


def summarize(rows):
    targets = {
        alias: {"occurrences": 0, "referring_pages": [], "links": []}
        for alias in ALIASES
    }
    errors = []
    pages_audited = 0
    for page in rows:
        source = page["path"]
        if "error" in page:
            errors.append({"path": source, "error": page["error"]})
            continue
        pages_audited += 1
        for link in page.get("diagnosis_links", []):
            target = link.get("target")
            if target not in targets:
                continue
            item = targets[target]
            item["occurrences"] += 1
            item["referring_pages"].append(source)
            item["links"].append({
                "source": source,
                "href": link["href"],
                "anchor_text": link["text"],
            })
    for item in targets.values():
        item["referring_pages"] = sorted(set(item["referring_pages"]))
        item["links"].sort(key=lambda x: (x["source"], x["href"], x["anchor_text"]))
        item["referring_page_count"] = len(item["referring_pages"])
    return {
        "audit_type": "diagnosis_alias_link_inventory",
        "scope": "github_checkout_static_html_only",
        "live_http_redirect_or_canonical_verified": False,
        "external_backlinks_verified": False,
        "canonical_decision": "pending_live_and_external_evidence",
        "html_pages_audited": pages_audited,
        "html_read_errors": errors,
        "total_alias_link_occurrences": sum(t["occurrences"] for t in targets.values()),
        "targets": targets,
    }


if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    print(json.dumps(summarize(audit(root)), ensure_ascii=False, indent=2))
