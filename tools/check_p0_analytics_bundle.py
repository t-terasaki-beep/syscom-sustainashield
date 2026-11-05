#!/usr/bin/env python3
"""Pre-upload read-only content gate for the P0 one-line analytics repair.

Only run inside the existing authorized publication session, AFTER its lock
was claimed and backups were made over the real deployment channel. This tool
reads local files and performs fresh GET requests; it NEVER uploads,
changes the site, obtains a publish lock, or verifies operator authorization.
A PASS is evidence for one content gate, not permission to publish.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import prepare_live_analytics_patch as p0


def check_bundle(
    original_backup: bytes,
    candidate_html: bytes,
    sibling_backup: bytes,
    report: dict,
    live_html: bytes,
    live_etag: str,
    live_sibling: dict,
    live_asset: dict,
    *,
    expected_original_sha: str = p0.EXPECTED_ORIGINAL_SHA256,
    expected_sibling_sha: str = p0.EXPECTED_SIBLING_SHA256,
) -> dict:
    """Fail closed unless backup, candidate, report, and live agree exactly."""
    if len(original_backup) != p0.EXPECTED_ORIGINAL_SIZE or p0.sha256(original_backup) != expected_original_sha:
        raise p0.PreflightError("Deployment-channel original backup differs from approved HTML; STOP")
    if original_backup != live_html or live_etag != p0.EXPECTED_ETAG:
        raise p0.PreflightError("Live HTML/ETag changed since original backup; STOP")
    if len(sibling_backup) != p0.EXPECTED_SIBLING_SIZE or p0.sha256(sibling_backup) != expected_sibling_sha:
        raise p0.PreflightError("Sibling deployment-channel backup differs from approved baseline; STOP")
    if sibling_backup.count(p0.TAG) != 1 or sibling_backup.count(b"ss-analytics.js") != 1:
        raise p0.PreflightError("Sibling backup tracker count differs; STOP")
    if live_sibling.get("sha256") != p0.sha256(sibling_backup) or live_sibling.get("etag") != p0.EXPECTED_SIBLING_ETAG:
        raise p0.PreflightError("Sibling changed since backup; STOP")
    # Preflight alone cannot guarantee that the GA4 loader is still browser-loadable
    # when the authorized operator reaches the upload gate. Recheck the live asset
    # here, independently of the earlier preflight report; fail closed on drift.
    if not isinstance(live_asset, dict) or any((
        live_asset.get("status") != 200,
        live_asset.get("url") != p0.ASSET_URL,
        live_asset.get("mime") not in p0.VALID_SCRIPT_MIMES,
        live_asset.get("bytes") != p0.EXPECTED_ASSET_SIZE,
        live_asset.get("sha256") != p0.EXPECTED_ASSET_SHA256,
        live_asset.get("ga4_measurement_id_present") is not True,
    )):
        raise p0.PreflightError("Analytics JS fresh live evidence missing/changed; STOP")
    expected_candidate = p0.build_one_line_patch(original_backup, expected_sha256=expected_original_sha)
    if candidate_html != expected_candidate:
        raise p0.PreflightError("Candidate is not exactly the approved one-line insertion; STOP")
    if not isinstance(report, dict) or any((
        report.get("publication_status") != "NOT_PUBLISHED",
        report.get("source_url") != p0.URL,
        report.get("production_etag_at_read") != p0.EXPECTED_ETAG,
        report.get("original_sha256") != p0.sha256(original_backup),
        report.get("prepared_sha256") != p0.sha256(candidate_html),
        report.get("production_original_bytes") != len(original_backup),
        report.get("prepared_bytes") != len(candidate_html),
    )):
        raise p0.PreflightError("Preflight report does not match backups and candidate; STOP")
    return {
        "result": "BACKUP_CANDIDATE_LIVE_BYTES_MATCH",
        "original_sha256": p0.sha256(original_backup),
        "candidate_sha256": p0.sha256(candidate_html),
        "sibling_sha256": p0.sha256(sibling_backup),
        "fresh_analytics_asset_sha256": live_asset["sha256"],
        "analytics_asset_recheck_scope": "HTTP_CONTENT_ONLY_NOT_GA4_RECEIPT",
        "live_etag": live_etag,
        "publish_lock_verified_by_this_tool": False,
        "operator_approval_verified_by_this_tool": False,
        "ga4_event_receipt_verified": False,
        "published_by_this_tool": False,
        "next_step": "Operator independently checks existing publish lock and approval immediately before single-file upload; after publish verify HTTP/tag/event/sibling and release lock.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-backup", required=True, type=Path)
    parser.add_argument("--candidate-html", required=True, type=Path)
    parser.add_argument("--sibling-backup", required=True, type=Path)
    parser.add_argument("--preflight-json", required=True, type=Path)
    args = parser.parse_args()
    # GET again immediately before authorized manual publication. No write or FTP.
    live_html, live_etag = p0.fetch_live()
    live_sibling = p0.fetch_sibling_live()
    # Fresh GET is required inside the operator's existing publish session.
    # Any fetch/status/MIME/size/SHA failure stops before a PASS can be emitted.
    live_asset = p0.fetch_analytics_asset()
    result = check_bundle(
        args.original_backup.read_bytes(), args.candidate_html.read_bytes(),
        args.sibling_backup.read_bytes(), json.loads(args.preflight_json.read_text(encoding="utf-8")),
        live_html, live_etag, live_sibling, live_asset,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (p0.PreflightError, OSError, ValueError) as exc:
        raise SystemExit(f"STOP: no publication, content gate failed: {exc}")
