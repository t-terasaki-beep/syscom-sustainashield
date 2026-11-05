#!/usr/bin/env python3
"""Read-only audit of HTML <a href> links to the two photo-diagnosis URLs.

Scans only repository checkout (NOT the production host or external backlinks).
Does not change redirects, canonical, files, metadata, or analytics settings.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

ORIGIN = 'https://syscom-sustaina-shield.com'
TARGETS = ('/shindan.html', '/photo-diagnosis/')
EXCLUDE_DIRS = {'.git', '.venv', 'node_modules', 'dist', 'build', '__pycache__'}

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'a':
            for key, value in attrs:
                if key.lower() == 'href' and value:
                    self.hrefs.append(value)


def target_for_href(source_path: str, href: str) -> str | None:
    """Classify direct in-domain links; do not follow redirects or guess JS links."""
    absolute = urlsplit(urljoin(ORIGIN + source_path, href))
    if absolute.scheme != 'https' or absolute.netloc.lower() != 'syscom-sustaina-shield.com':
        return None
    path = unquote(absolute.path)
    if path == '/photo-diagnosis/index.html':
        path = '/photo-diagnosis/'
    return path if path in TARGETS else None


def source_url_path(root: Path, file: Path) -> str:
    path = '/' + file.relative_to(root).as_posix()
    if path.endswith('/index.html'):
        return path[:-10]
    return path


def audit(root: Path) -> dict:
    root = root.resolve()
    result = {
        'scope': 'repository HTML only; not live production, sitemap, Google Search Console, or external backlinks',
        'redirect_or_canonical_changes': 0,
        'html_files_scanned': 0,
        'counts': {t: 0 for t in TARGETS},
        'sources': [],
        'decode_errors': [],
    }
    for file in sorted(root.rglob('*.html')):
        relative = file.relative_to(root)
        if any(part in EXCLUDE_DIRS for part in relative.parts[:-1]):
            continue
        result['html_files_scanned'] += 1
        try:
            html = file.read_text(encoding='utf-8')
        except UnicodeError:
            result['decode_errors'].append(relative.as_posix())
            continue
        parser = LinkParser()
        parser.feed(html)
        source = source_url_path(root, file)
        hits = []
        for href in parser.hrefs:
            target = target_for_href(source, href)
            if target:
                result['counts'][target] += 1
                hits.append({'href': href, 'target': target})
        if hits:
            result['sources'].append({'file': relative.as_posix(), 'matches': hits})
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', default='.', help='repository checkout root')
    args = parser.parse_args()
    print(json.dumps(audit(Path(args.root)), ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
