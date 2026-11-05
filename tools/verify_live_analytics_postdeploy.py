#!/usr/bin/env python3
"""P0 one-line analytics patch: read-only post-publication byte verification.

Does not upload, publish, unlock, or prove GA4 event delivery.
Run only from the authorized publication session AFTER the separately approved,
locked and backed-up one-file deployment. Sibling SHA-256 captured immediately
before publication is mandatory to prove that the other article was untouched.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

TARGET = "https://syscom-sustaina-shield.com/column/chiba-suigai-hinanjo-dengen/"
SIBLING = "https://syscom-sustaina-shield.com/column/shoene2024-data-leak-alert/"
ORIGINAL_ETAG = "6262-65f3790c0687e"
ORIGINAL_SHA256 = "aa03d76ae747abb7ff841b8db49d00cf001f720b6e0cb10ed8ad634c5f1abd81"
# Independently observed unchanged sibling: 2026-11-03 production GET baseline.
# The operator-supplied under-lock hash alone must NOT be allowed to authorize
# an already-modified sibling as its own clean reference.
SIBLING_APPROVED_SHA256 = "2a7af2f43473f03c58ffca47b284b4fdc9b9ca97779e4b2486f237746672bbd6"
PATCHED_SIZE = 25239
TAG = b'<script src="/assets/ss-analytics.js" defer></script>'
TARGET_FOOTER = b"</script>\n" + TAG + b"</body></html>\n"
ANALYTICS_ASSET = "https://syscom-sustaina-shield.com/assets/ss-analytics.js"
ANALYTICS_ASSET_MAX_BYTES = 65536
GA4_MEASUREMENT_ID = b"G-ELZG7B45NH"
# Actual production delivery verified via GET-only Actions 41884024682,
# 2026-11-05 03:08 JST. Any byte drift requires manual re-baselining.
ANALYTICS_ASSET_EXPECTED_SIZE = 8607
ANALYTICS_ASSET_EXPECTED_SHA256 = "d31313584ab615a35581de2d8ccd9e4380cb95f14133b174269bca4d761f9ed3"
# A 200 response with the right GA4 ID is insufficient if the browser refuses to execute it.
# A JavaScript media type is required; HTML/text fallback must not be marked verified.
JAVASCRIPT_MEDIA_TYPES = frozenset({
    "text/javascript", "application/javascript", "text/ecmascript",
    "application/ecmascript", "application/x-javascript",
})


class VerificationError(ValueError):
    pass


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def strong_etag(raw: str | None) -> str:
    if not raw or raw.startswith("W/") or not re.fullmatch(r'"[^"]+"', raw.strip()):
        raise VerificationError("Missing, weak, or malformed ETag: cannot verify production revision")
    return raw.strip()[1:-1]


def check_target(raw: bytes, etag: str) -> dict:
    """Prove that the live HTML is the exact baseline plus the approved tag."""
    if len(raw) != PATCHED_SIZE:
        raise VerificationError(f"P0 target size changed: {len(raw)} != {PATCHED_SIZE}")
    if etag == ORIGINAL_ETAG:
        raise VerificationError("Old ETag still served; publication unverified")
    if raw.count(TAG) != 1 or raw.count(b"ss-analytics.js") != 1:
        raise VerificationError("P0 target analytics tag not present exactly once")
    if not raw.endswith(TARGET_FOOTER):
        raise VerificationError("P0 target footer differs from approved one-line patch")
    if raw.lower().count(b"<h1") < 1 or b"</h1>" not in raw.lower():
        raise VerificationError("P0 target H1 is missing")
    restored = raw.replace(TAG, b"", 1)
    if sha256(restored) != ORIGINAL_SHA256:
        raise VerificationError("P0 target content differs beyond the approved one-line insertion")
    return {"status": "PASS", "http": 200, "bytes": len(raw), "etag": etag,
            "sha256": sha256(raw), "analytics_tag_count": 1,
            "original_restored_sha256": sha256(restored)}


def check_sibling(raw: bytes, etag: str, baseline_sha: str) -> dict:
    if not re.fullmatch(r"[a-f0-9]{64}", baseline_sha):
        raise VerificationError("Sibling baseline SHA-256 must be exactly 64 lowercase hex chars")
    if baseline_sha != SIBLING_APPROVED_SHA256:
        raise VerificationError("Sibling before-upload baseline differs from independently approved production SHA-256; STOP")
    current_sha = sha256(raw)
    if current_sha != baseline_sha:
        raise VerificationError("Sibling article changed since pre-publication snapshot")
    if raw.count(TAG) != 1:
        raise VerificationError("Sibling article analytics tag is not exactly once")
    return {"status": "PASS", "http": 200, "bytes": len(raw), "etag": etag,
            "sha256": current_sha, "analytics_tag_count": 1}


def fetch_exact(url: str, max_bytes: int) -> tuple[bytes, str]:
    req = Request(url, headers={"Cache-Control": "no-cache", "Pragma": "no-cache",
                                "Accept-Encoding": "identity", "User-Agent": "SustainaShield-P0-Verify/1.0"})
    with urlopen(req, timeout=20) as res:
        if res.status != 200 or res.geturl() != url:
            raise VerificationError(f"Wrong status or redirected URL for {url}")
        etag = strong_etag(res.headers.get("ETag"))
        blob = res.read(max_bytes + 1)
    if len(blob) > max_bytes:
        raise VerificationError(f"Response exceeded {max_bytes} bytes for {url}")
    return blob, etag


def check_analytics_asset(raw: bytes, content_type: str | None) -> dict:
    """Verify browser-loadable JavaScript delivery, not GA4 event receipt."""
    mime = (content_type or "").split(";", 1)[0].strip().lower()
    if mime not in JAVASCRIPT_MEDIA_TYPES:
        raise VerificationError("Analytics asset has missing/non-JavaScript Content-Type; STOP")
    if not raw or len(raw) > ANALYTICS_ASSET_MAX_BYTES:
        raise VerificationError("Analytics asset empty or unexpectedly large; STOP")
    if raw.lstrip().lower().startswith((b"<!doctype html", b"<html")):
        raise VerificationError("Analytics asset returned an HTML page; STOP")
    if GA4_MEASUREMENT_ID not in raw:
        raise VerificationError("Analytics asset missing the expected GA4 ID; STOP")
    if len(raw) != ANALYTICS_ASSET_EXPECTED_SIZE:
        raise VerificationError("Analytics asset size differs from verified production baseline; STOP")
    if sha256(raw) != ANALYTICS_ASSET_EXPECTED_SHA256:
        raise VerificationError("Analytics asset SHA-256 differs from verified production baseline; STOP")
    return {"status": "PASS", "http": 200, "bytes": len(raw),
            "sha256": sha256(raw), "sha256_matches_production_baseline": True,
            "javascript_content_type": mime,
            "ga4_measurement_id_present": True,
            "ga4_event_receipt_verified": False}


def fetch_analytics_asset() -> dict:
    """GET only; reject redirects and avoid exposing the script body in logs."""
    req = Request(ANALYTICS_ASSET, headers={
        "Cache-Control": "no-cache", "Pragma": "no-cache",
        "Accept-Encoding": "identity", "User-Agent": "SustainaShield-P0-Verify/1.0"})
    with urlopen(req, timeout=20) as res:
        if res.status != 200 or res.geturl() != ANALYTICS_ASSET:
            raise VerificationError("Analytics asset not HTTP 200 at the expected URL")
        content_type = res.headers.get("Content-Type")
        raw = res.read(ANALYTICS_ASSET_MAX_BYTES + 1)
    return check_analytics_asset(raw, content_type)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sibling-before-sha256", required=True,
                        help="Sibling HTML SHA-256 captured under publish lock before upload")
    parser.add_argument("--evidence-json", type=Path,
                        help="Optional local evidence file (exclusive create; never overwrites). Not GA4 event proof.")
    args = parser.parse_args()
    if args.evidence_json is not None and args.evidence_json.exists():
        raise VerificationError("Evidence JSON already exists; refusing overwrite")
    if not re.fullmatch(r"[a-f0-9]{64}", args.sibling_before_sha256):
        raise VerificationError("Invalid sibling baseline SHA-256")
    target, target_etag = fetch_exact(TARGET, 25300)
    sibling, sibling_etag = fetch_exact(SIBLING, 300000)
    asset = fetch_analytics_asset()
    result = {"publication_verification": "PASS_FOR_HTTP_CONTENT_ONLY",
              "observed_at_utc": datetime.now(timezone.utc).isoformat(),
              "evidence_scope": "POSTDEPLOY_HTTP_BYTES_ONLY_GA4_EVENT_UNVERIFIED",
              "target": check_target(target, target_etag),
              "sibling_unchanged": check_sibling(sibling, sibling_etag, args.sibling_before_sha256),
              "analytics_asset_http_check": asset,
              "ga4_page_view_delivery_verified": False,
              "ga4_check_required": "Confirm GA4 real-time page_view receipt in authorized session",
              "publish_and_ftp_operations": 0}
    # The authorized operator may retain this GET-only evidence locally, beside
    # (not inside) the deployment backup. Exclusive creation avoids overwriting
    # a previous verification record; stdout remains the default behavior.
    # GA4 event receipt must be recorded separately by the authorized operator.
    if args.evidence_json is not None:
        with args.evidence_json.open("x", encoding="utf-8") as evidence:
            json.dump(result, evidence, ensure_ascii=False, indent=2)
            evidence.write("\\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (VerificationError, OSError) as exc:
        raise SystemExit(f"STOP: verification not completed: {exc}")
