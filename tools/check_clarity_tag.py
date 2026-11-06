#!/usr/bin/env python3
"""Static preflight check for Clarity installation. No network or personal data."""
from pathlib import Path
import sys

PROJECT_ID = "z7exxosjzy"
TAG = "https://www.clarity.ms/tag/"
def check(html: str) -> list[str]:
    issues = []
    if html.count(TAG) != 1:
        issues.append(f"Clarity loader count must be 1; found {html.count(TAG)}")
    if html.count('"' + PROJECT_ID + '"') != 1:
        issues.append("Expected Clarity project ID not found exactly once")
    if "<head>" not in html or "</head>" not in html:
        issues.append("Missing head")
    elif TAG not in html.split("</head>", 1)[0]:
        issues.append("Clarity loader is not inside head")
    return issues

if __name__ == "__main__":
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "index.html")
    issues = check(target.read_text(encoding="utf-8"))
    if issues:
        print("FAIL:", "; ".join(issues))
        sys.exit(1)
    print("PASS: Clarity tag appears exactly once inside head")
