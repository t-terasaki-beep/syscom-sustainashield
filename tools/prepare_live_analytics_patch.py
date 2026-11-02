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
from pathlib import Path
from urllib.request import Request, urlopen

URL = "https://syscom-sustaina-shield.com/column/chiba-suigai-hinanjo-dengen/"
EXPECTED_ETAG = "6262-65f3790c0687e"
EXPECTED_ORIGINAL_SIZE = 25186
EXPECTED_PATCHED_SIZE = 25239
TAG = b'<script src="/assets/ss-analytics.js" defer></script>'
SUFFIX = b"</script></body></html>"


class PreflightError(ValueError):
    pass


def normalize_etag(value: str | None) -> str:
    # Weak validators do not prove byte identity. Fail closed.
    if not value or value.startswith("W/"):
        raise PreflightError("Missing/weak HTTP ETag; cannot safely prepare patch")
    return value.strip('"')


def build_one_line_patch(raw: bytes) -> bytes:
    """Fail closed unless the live bytes have the exact expected structure."""
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
    changed = raw[:-len(b"</body></html>")] + TAG + b"</body></html>"
    if len(changed) != EXPECTED_PATCHED_SIZE:
        raise PreflightError("Patched size mismatch")
    if changed.count(TAG) != 1:
        raise PreflightError("Expected exactly one analytics tag")
    # Byte-for-byte proof that the patch is only a single insertion.
    position = len(raw) - len(b"</body></html>")
    if changed[:position] != raw[:position] or changed[position + len(TAG):] != raw[position:]:
        raise PreflightError("Unexpected differences beyond one insertion")
    return changed


def fetch_live() -> tuple[bytes, str]:
    request = Request(URL, headers={
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
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
