#!/usr/bin/env python3
"""P2旧屋号の再混入を検知する静的検査（16ページ限定・本番操作なし）。

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
    return {
        "scope": "PR #19 P2 review-only HTML files; NOT production or site-wide coverage",
        "checked_pages": len(PAGES),
        "checked_generators": 1,
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
