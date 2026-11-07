#!/usr/bin/env python3
"""P2旧屋号・住宅LINEの再混入を検知する静的検査（17ページ限定・本番操作なし）。

PR #19のレビュー候補だけを検査する。全サイトの旧表記ゼロは主張しない。
株式会社シスコムネットなど法的な法人表示は検査で禁止しない。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PAGES = (
    "chiba-ene-lab/index.html",
    "chiba-land-search/index.html",
    "company.html",
    "contact.html",
    "faq.html",
    "flow.html",
    "grid-battery/index.html",
    "tools/publish/lp-media-set-v1/column/heat-and-solar/index.html",
    "tools/publish/lp-media-set-v1/column/ohisama-compare/index.html",
    "lp/gaichu-block/index.html",
    "lp/index.html",
    "privacy.html",
    "service.html",
    "shanetsu-chiba/index.html",
    "simulator/index.html",
    "sotsu-fit/index.html",
    "terasaki_lp.html",
    "voice.html",
)
OLD_BRANDS = ("シスコムサステナシールド", "SYSCOM SUSTAINA SHIELD")
CURRENT_BRAND = "サステナシールド"


def check_text(text: str) -> list[str]:
    errors = [f"旧屋号 {brand!r} が {text.count(brand)} 件" for brand in OLD_BRANDS
              if brand in text]
    if CURRENT_BRAND not in text:
        errors.append("正式表記サステナシールドがない")
    return errors


def audit(root: Path) -> dict:
    errors: list[dict[str, object]] = []
    for relative in PAGES:
        path = root / relative
        try:
            body = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append({"path": relative, "issues": [type(exc).__name__]})
            continue
        issues = check_text(body)
        if relative == "tools/publish/lp-media-set-v1/column/heat-and-solar/index.html":
            # Review-only generated source: do not equate this with the live page.
            # Header, text link and in-article CTA should all use residential LINE.
            if "631cqlgf" in body:
                issues.append("屋根遮熱と太陽光コラムに住宅LINEの旧IDが残存")
            if body.count('href="https://line.me/R/ti/p/%40829oslez"') != 3:
                issues.append("屋根遮熱と太陽光コラムのLINEリンク3本が正本@829oslezに統一されていない")
            if 'https://line.me/R/ti/p/%40829oslez</a>' not in body:
                issues.append("屋根遮熱と太陽光コラムの表示LINE URLが正本と不一致")
        if relative == "tools/publish/lp-media-set-v1/column/ohisama-compare/index.html":
            # Existing generated HTML is a separate delivery artifact from the
            # corrected build_column.py generator. Check the visible URL and
            # all three actual LINE link destinations (header/text/CTA).
            if "631cqlgf" in body:
                issues.append("おひさま比較記事に住宅LINEの旧IDが残存")
            if body.count('href="https://line.me/R/ti/p/%40829oslez"') != 3:
                issues.append("おひさま比較記事のLINEリンク3本が正本@829oslezに統一されていない")
        if issues:
            errors.append({"path": relative, "issues": issues})
    # Source-of-truth for future /column/ output. Never regenerate or publish
    # production-only articles as part of this static audit.
    generator_path = "tools/publish/lp-media-set-v1/column/build_column.py"
    try:
        generator = (root / generator_path).read_text(encoding="utf-8")
        template_issues = check_text(generator)
        if "%40631cqlgf" in generator:
            template_issues.append("住宅LINEの旧アカウントIDが残存")
        if generator.count("%40829oslez") != 2:
            template_issues.append("住宅LINEの正本リンクがヘッダーと記事CTAの2箇所に揃っていない")
    except (OSError, UnicodeError) as exc:
        template_issues = [type(exc).__name__]
    if template_issues:
        errors.append({"path": generator_path, "issues": template_issues})
    # The /download/ lead form is a distinct template (not one of the 16 P2 pages).
    # Its post-submit LINE handoff must point to the approved residential account.
    download_path = "tools/publish/lp-media-set-v1/download/index.html"
    try:
        download = (root / download_path).read_text(encoding="utf-8")
        download_issues = check_text(download)
        if "%40631cqlgf" in download or "@631cqlgf" in download:
            download_issues.append("資料請求完了後のLINEに住宅旧IDが残存")
        if download.count("https://line.me/R/ti/p/%40829oslez") != 1:
            download_issues.append("資料請求完了後のLINEリンクは正本@829oslezを1箇所だけ使用すること")
    except (OSError, UnicodeError) as exc:
        download_issues = [type(exc).__name__]
    if download_issues:
        errors.append({"path": download_path, "issues": download_issues})
    # Shared media metadata feeds many pages: a renamed HTML title alone cannot
    # prevent the old company-guide label from reappearing in generated cards.
    media_map_path = "tools/publish/lp-media-set-v1/media-map.json"
    try:
        media_map_text = (root / media_map_path).read_text(encoding="utf-8")
        media_map_issues = [
            f"旧屋号 {brand!r} が {media_map_text.count(brand)} 件"
            for brand in OLD_BRANDS if brand in media_map_text
        ]
        media_map = json.loads(media_map_text)
        title = media_map["docs"]["company-guide"]["title"]
        if title != "サステナシールド 会社・サービス案内":
            media_map_issues.append("company-guide の表示名が正式屋号と一致しない")
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        media_map_issues = [type(exc).__name__]
    if media_map_issues:
        errors.append({"path": media_map_path, "issues": media_map_issues})
    return {
        "scope": "PR #19 P2 review-only HTML files; NOT production or site-wide coverage",
        "checked_pages": len(PAGES),
        "checked_generators": 1,
        "checked_download_templates": 1,
        "checked_media_maps": 1,
        "failed_media_maps": sum(1 for row in errors if row["path"] == media_map_path),
        "failed_download_templates": sum(1 for row in errors if row["path"] == download_path),
        "failed_pages": sum(1 for row in errors if row["path"] in PAGES),
        "failed_generators": sum(1 for row in errors if row["path"] == generator_path),
        "errors": errors,
        "production_reads": 0,
        "production_writes": 0,
        "pass": not errors,
    }


def main() -> int:
    result = audit(Path(__file__).resolve().parents[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
