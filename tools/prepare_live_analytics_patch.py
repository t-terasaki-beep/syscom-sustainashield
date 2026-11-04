#!/usr/bin/env python3
"""Read-only HTTP preflight + local one-line analytics patch preparation.

IMPORTANT: This tool NEVER uploads or publishes. Publication must use the
separately authorized, locked, backed-up production workflow and a second
ETag/SHA comparison immediately before upload.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

URL = "https://syscom-sustaina-shield.com/column/chiba-suigai-hinanjo-dengen/"
EXPECTED_ETAG = "6262-65f3790c0687e"
EXPECTED_ORIGINAL_SIZE = 25186
EXPECTED_PATCHED_SIZE = 25239
TAG = b'<script src="/assets/ss-analytics.js" defer></script>'
SUFFIX = b"</script>\n</body></html>\n"
EXPECTED_ORIGINAL_SHA256 = "aa03d76ae747abb7ff841b8db49d00cf001f720b6e0cb10ed8ad634c5f1abd81"


class PreflightError(ValueError):
    pass


def normalize_etag(value: str | None) -> str:
    # A strong HTTP entity-tag must be fully enclosed in quotes. An unquoted
    # token is not a valid strong validator even if its bytes match our pin.
    if not value or not re.fullmatch(r'"[^"]+"', value.strip()):
        raise PreflightError("Missing, weak, or malformed HTTP ETag; STOP")
    return value.strip()[1:-1]


def build_one_line_patch(raw: bytes, *, expected_sha256: str = EXPECTED_ORIGINAL_SHA256) -> bytes:
    """Fail closed unless the complete source bytes match an approved baseline.

    The override is for offline fixtures. Production callers must keep the pinned
    baseline default, including if this helper is invoked without fetch_live().
    """
    if len(raw) != EXPECTED_ORIGINAL_SIZE:
        raise PreflightError(f"Unexpected original size: {len(raw)} != {EXPECTED_ORIGINAL_SIZE}")
    if b"ss-analytics.js" in raw:
        raise PreflightError("Analytics reference already exists; no patch prepared")
    # A different GA4 loader/config may already track this page. Fail closed
    # instead of adding a second page_view source to the existing production HTML.
    other_trackers = (
        b"googletagmanager.com/gtag/js",
        b"googletagmanager.com/gtm.js",
        b"gtag('config'",
        b'gtag("config"',
        b"G-ELZG7B45NH",
    )
    if any(marker in raw for marker in other_trackers):
        raise PreflightError("Other GA4/GTM tracking detected; manual review required. STOP")
    if b"<h1" not in raw.lower() or b"</h1>" not in raw.lower():
        raise PreflightError("Article H1 missing; wrong or damaged live page. STOP")
    if raw.count(b"</body>") != 1 or not raw.endswith(SUFFIX):
        raise PreflightError("Unexpected body/footer structure; no patch prepared")
    # Guard the builder itself, not only fetch_live(): a stale/unapproved file
    # with identical length, H1 and footer must never yield a publish candidate.
    if sha256(raw) != expected_sha256:
        raise PreflightError("Original SHA-256 differs from approved live baseline. STOP")
    # Production has a newline after </script> and after </html>; keep both bytes.
    position = len(raw) - len(b"</body></html>\n")
    changed = raw[:position] + TAG + raw[position:]
    if len(changed) != EXPECTED_PATCHED_SIZE:
        raise PreflightError("Patched size mismatch")
    if changed.count(TAG) != 1:
        raise PreflightError("Expected exactly one analytics tag")
    # Byte-for-byte proof that the patch is only a single insertion.
    if changed[:position] != raw[:position] or changed[position + len(TAG):] != raw[position:]:
        raise PreflightError("Unexpected differences beyond one insertion")
    return changed


def fetch_live() -> tuple[bytes, str]:
    request = Request(URL, headers={
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Accept-Encoding": "identity",
        "User-Agent": "SustainaShield-Preflight/1.0",
    })
    with urlopen(request, timeout=20) as response:
        if response.status != 200 or response.geturl() != URL:
            raise PreflightError("Not HTTP 200 from exact expected URL")
        etag = normalize_etag(response.headers.get("ETag"))
        if etag != EXPECTED_ETAG:
            raise PreflightError(f"Production ETag changed: {etag!r}. STOP and re-baseline")
        payload = response.read(EXPECTED_ORIGINAL_SIZE + 1)
    if len(payload) != EXPECTED_ORIGINAL_SIZE:
        raise PreflightError("Production byte size changed. STOP and re-baseline")
    if sha256(payload) != EXPECTED_ORIGINAL_SHA256:
        raise PreflightError("Production SHA-256 changed. STOP and re-baseline")
    return payload, etag


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True,
                        help="Private local output folder; NEVER upload it directly")
    args = parser.parse_args()

    raw, etag = fetch_live()
    changed = build_one_line_patch(raw)
    dest = Path(args.output_dir).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    html_path = dest / "index.html"
    report_path = dest / "preflight.json"
    if html_path.exists() or report_path.exists():
        raise PreflightError("Output files exist; refusing overwrite")
    report = {
        "publication_status": "NOT_PUBLISHED",
        "source_url": URL,
        "production_etag_at_read": etag,
        "production_original_bytes": len(raw),
        "prepared_bytes": len(changed),
        "original_sha256": sha256(raw),
        "prepared_sha256": sha256(changed),
        "change": "insert exactly one ss-analytics.js script before </body>",
        "mandatory_next_steps": [
            "Claim production publish lock with existing authorized workflow",
            "Backup production via deployment channel and compare live SHA/ETag again",
            "Upload this one file only after explicit approval; never publish repo-generated page",
            "Verify HTTP 200, exactly one tag, pageview event, and unchanged sibling page",
            "Release publish lock and retain rollback backup",
        ],
    }
    html_path.write_bytes(changed)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps({"local_preflight": "PASS", "published": False,
                      "report": str(report_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (PreflightError, OSError) as exc:
        raise SystemExit(f"STOP (no publication): {exc}")
