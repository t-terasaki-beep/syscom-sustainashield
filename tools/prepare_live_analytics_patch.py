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
SIBLING_URL = "https://syscom-sustaina-shield.com/column/shoene2024-data-leak-alert/"
EXPECTED_SIBLING_ETAG = "5d57-65f3744b854f4"
EXPECTED_SIBLING_SIZE = 23895
EXPECTED_SIBLING_SHA256 = "2a7af2f43473f03c58ffca47b284b4fdc9b9ca97779e4b2486f237746672bbd6"
EXPECTED_ETAG = "6262-65f3790c0687e"
EXPECTED_ORIGINAL_SIZE = 25186
EXPECTED_PATCHED_SIZE = 25239
TAG = b'<script src="/assets/ss-analytics.js" defer></script>'
SUFFIX = b"</script>\n</body></html>\n"
EXPECTED_ORIGINAL_SHA256 = "aa03d76ae747abb7ff841b8db49d00cf001f720b6e0cb10ed8ad634c5f1abd81"
# P0 production JS baseline observed in read-only GitHub Actions on 2026-11-05.
# A valid script response is necessary before preparing any local patch.
ASSET_URL = "https://syscom-sustaina-shield.com/assets/ss-analytics.js"
EXPECTED_ASSET_SIZE = 8607
EXPECTED_ASSET_SHA256 = "d31313584ab615a35581de2d8ccd9e4380cb95f14133b174269bca4d761f9ed3"
GA4_MEASUREMENT_ID = b"G-ELZG7B45NH"
VALID_SCRIPT_MIMES = frozenset((
    "text/javascript", "application/javascript", "text/ecmascript",
    "application/ecmascript", "application/x-javascript",
))


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


def validate_sibling_snapshot(raw: bytes, etag: str) -> dict:
    """Fail closed on sibling drift BEFORE preparing any local candidate.

    The fixed reference is the independently observed production sibling from
    2026-11-03. A preflight snapshot is NOT a substitute for the under-lock
    SHA-256 snapshot taken immediately before the authorized publication.
    """
    if etag != EXPECTED_SIBLING_ETAG:
        raise PreflightError("Sibling ETag changed; manual review required. STOP")
    if len(raw) != EXPECTED_SIBLING_SIZE:
        raise PreflightError("Sibling size changed; manual review required. STOP")
    digest = sha256(raw)
    if digest != EXPECTED_SIBLING_SHA256:
        raise PreflightError("Sibling SHA-256 changed; manual review required. STOP")
    if raw.count(TAG) != 1 or raw.count(b"ss-analytics.js") != 1:
        raise PreflightError("Sibling analytics tag count differs from baseline. STOP")
    if not raw.rstrip().endswith(b"</html>"):
        raise PreflightError("Sibling HTML footer incomplete. STOP")
    return {
        "url": SIBLING_URL, "etag": etag, "bytes": len(raw),
        "sha256": digest, "analytics_tag_count": 1,
        "capture_stage": "PREFLIGHT_ONLY_NOT_UNDER_LOCK",
    }


def fetch_sibling_live() -> dict:
    """GET-only sibling check; never copy or modify the live sibling page."""
    request = Request(SIBLING_URL, headers={
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Accept-Encoding": "identity",
        "User-Agent": "SustainaShield-Preflight/1.0",
    })
    with urlopen(request, timeout=20) as response:
        if response.status != 200 or response.geturl() != SIBLING_URL:
            raise PreflightError("Sibling not HTTP 200 from exact URL; STOP")
        etag = normalize_etag(response.headers.get("ETag"))
        payload = response.read(EXPECTED_SIBLING_SIZE + 1)
    return validate_sibling_snapshot(payload, etag)


def validate_analytics_asset(raw: bytes, *, content_type: str | None,
                             status: int = 200, actual_url: str = ASSET_URL) -> dict:
    """Do not prepare a patch when the browser cannot load the pinned GA4 script.

    An asset check verifies HTTP delivery only. It does NOT verify receipt of a
    GA4 event or authorize a production write.
    """
    mime = (content_type or "").split(";", 1)[0].strip().lower()
    if status != 200 or actual_url != ASSET_URL:
        raise PreflightError("Analytics JS HTTP status or final URL changed. STOP")
    if mime not in VALID_SCRIPT_MIMES:
        raise PreflightError("Analytics JS Content-Type is not JavaScript. STOP")
    if len(raw) != EXPECTED_ASSET_SIZE:
        raise PreflightError("Analytics JS byte size changed. STOP")
    digest = sha256(raw)
    if digest != EXPECTED_ASSET_SHA256:
        raise PreflightError("Analytics JS SHA-256 changed. STOP")
    if raw.lstrip().lower().startswith((b"<!doctype html", b"<html")):
        raise PreflightError("Analytics JS resolved to HTML. STOP")
    if GA4_MEASUREMENT_ID not in raw:
        raise PreflightError("Analytics JS GA4 measurement ID missing. STOP")
    return {
        "url": ASSET_URL, "status": status, "mime": mime,
        "bytes": len(raw), "sha256": digest,
        "ga4_measurement_id_present": True,
        "capture_stage": "PREFLIGHT_ONLY_NOT_UNDER_LOCK",
        "ga4_event_receipt_verified": False,
    }


def fetch_analytics_asset() -> dict:
    """GET-only asset verification before writing any local candidate."""
    request = Request(ASSET_URL, headers={
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Accept-Encoding": "identity",
        "User-Agent": "SustainaShield-Preflight/1.0",
    })
    with urlopen(request, timeout=20) as response:
        status, final_url = response.status, response.geturl()
        content_type = response.headers.get("Content-Type")
        payload = response.read(EXPECTED_ASSET_SIZE + 1)
    return validate_analytics_asset(
        payload, content_type=content_type, status=status, actual_url=final_url
    )


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()



def write_local_preflight_outputs(dest: Path, changed: bytes, report: dict) -> Path:
    """Create the local patch and JSON without an overwrite race.

    An exists() precheck alone cannot protect against concurrent scheduled runs.
    Exclusive create ('x') refuses an existing file or symlink even if it
    appears between precheck and open. Nothing here uploads or publishes.
    """
    dest.mkdir(parents=True, exist_ok=True)
    html_path, report_path = dest / "index.html", dest / "preflight.json"
    if html_path.exists() or report_path.exists():
        raise PreflightError("Output files exist; refusing overwrite")

    html_created = False
    report_created = False
    try:
        with html_path.open("xb") as html:
            html_created = True
            html.write(changed)
        with report_path.open("x", encoding="utf-8") as evidence:
            report_created = True
            json.dump(report, evidence, ensure_ascii=False, indent=2)
            evidence.write("\n")
    except BaseException:
        # Roll back only the files exclusively created by this invocation.
        if report_created:
            report_path.unlink(missing_ok=True)
        if html_created:
            html_path.unlink(missing_ok=True)
        raise
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True,
                        help="Private local output folder; NEVER upload it directly")
    args = parser.parse_args()

    raw, etag = fetch_live()
    changed = build_one_line_patch(raw)
    sibling = fetch_sibling_live()  # Fail closed before writing any candidate files.
    asset = fetch_analytics_asset()  # A missing/altered JS must not yield preflight PASS.
    dest = Path(args.output_dir).resolve()
    report = {
        "publication_status": "NOT_PUBLISHED",
        "source_url": URL,
        "production_etag_at_read": etag,
        "production_original_bytes": len(raw),
        "prepared_bytes": len(changed),
        "original_sha256": sha256(raw),
        "prepared_sha256": sha256(changed),
        "sibling_read_only_preflight": sibling,
        "analytics_asset_read_only_preflight": asset,
        "change": "insert exactly one ss-analytics.js script before </body>",
        "mandatory_next_steps": [
            "Claim production publish lock with existing authorized workflow",
            "Backup production via deployment channel and compare live SHA/ETag again",
            "Re-capture sibling SHA under publish lock immediately before upload; do not reuse this earlier preflight snapshot",
            "Upload this one file only after explicit approval; never publish repo-generated page",
            "Verify HTTP 200, exactly one tag, pageview event, and unchanged sibling page",
            "Release publish lock and retain rollback backup",
        ],
    }
    report_path = write_local_preflight_outputs(dest, changed, report)
    print(json.dumps({"local_preflight": "PASS", "published": False,
                      "report": str(report_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (PreflightError, OSError) as exc:
        raise SystemExit(f"STOP (no publication): {exc}")
