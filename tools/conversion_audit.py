#!/usr/bin/env python3
"""Read-only static conversion audit for Sustainashield HTML pages.
No credentials, network requests, analytics claims, or production changes.
"""
from pathlib import Path
import posixpath
from html.parser import HTMLParser
import json
import sys

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = False
        self.title_text = ""
        self.links = []
        # Track only the active anchor: text outside </a> is never CTA text.
        self.active_link = None
        self.forms = 0
        self.placeholder_forms = 0
        self.inputs = []
        self.meta_description = False
        self.description = ""
        self.headings = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title": self.title = True
        if tag == "h1": self.headings += 1
        if tag == "a":
            self.active_link = {"href": a.get("href", ""), "text": ""}
            self.links.append(self.active_link)
        if tag == "form":
            self.forms += 1
            # A known unimplemented inline submit handler blocks real inquiries.
            # Heuristic only: do not classify arbitrary AJAX "return false" as broken.
            handler = (a.get("onsubmit") or "").lower()
            stub_markers = ("送信先", "実装してください", "未実装",
                            "not implemented", "coming soon", "placeholder")
            if "return false" in handler and any(w in handler for w in stub_markers):
                self.placeholder_forms += 1
        if tag in ("input", "textarea"): self.inputs.append(a.get("name", ""))
        if tag == "meta" and a.get("name", "").lower() == "description":
            self.description = a.get("content", "")

    def handle_endtag(self, tag):
        if tag == "title": self.title = False
        if tag == "a": self.active_link = None

    def handle_data(self, data):
        if self.title: self.title_text += data.strip()
        if self.active_link is not None:
            self.active_link["text"] += data.strip()

def is_placeholder_cta_href(link):
    """Flag obvious non-navigation CTA targets; do not assert a JS handler is broken."""
    href = (link["href"] or "").strip().lower()
    is_cta_text = any(word in link["text"] for word in ("相談", "問い合わせ", "見積"))
    return is_cta_text and href in ("", "#", "#!", "javascript:void(0)", "javascript:void(0);")

def is_self_referential_cta(link, page_path):
    """Identify CTA anchors that only navigate back to the same HTML page.

    This is a static routing warning, not a claim about browser-side handlers.
    """
    href = (link["href"] or "").strip()
    if not any(word in link["text"] for word in ("相談", "問い合わせ", "見積")):
        return False
    if not href or href.startswith(("//", "#")):
        return False
    if ":" in href.split("/", 1)[0]:
        return False  # schemes such as tel:, https:, mailto:, javascript:
    route = href.split("#", 1)[0].split("?", 1)[0]
    if not route:
        return False
    target = (posixpath.normpath(route.lstrip("/")) if route.startswith("/")
              else posixpath.normpath(posixpath.join(posixpath.dirname(page_path), route)))
    return target == page_path


def audit(root):
    results = []
    for path in sorted(root.rglob("*.html")):
        if ".git" in path.parts: continue
        page = Page()
        try:
            page.feed(path.read_text(encoding="utf-8"))
            placeholder_links = [x for x in page.links if is_placeholder_cta_href(x)]
            page_path = path.relative_to(root).as_posix()
            self_links = [x for x in page.links if is_self_referential_cta(x, page_path)]
            ctas = [
                x for x in page.links
                if not is_placeholder_cta_href(x)
                and not is_self_referential_cta(x, page_path)
                and (
                    (x["href"] or "").startswith(("tel:", "mailto:", "https://line.me/", "https://lin.ee/"))
                    or (
                        bool((x["href"] or "").strip())
                        and not (x["href"] or "").strip().lower().startswith("javascript:")
                        and any(w in x["text"] for w in ("相談", "問い合わせ", "見積"))
                    )
                )
            ]
            usable_forms = page.forms - page.placeholder_forms
            warnings = (
                (["no_title"] if not page.title_text else [])
                + (["no_meta_description"] if not page.description else [])
                + (["no_h1"] if not page.headings else [])
                + (["no_obvious_cta"] if not ctas and not usable_forms else [])
                + (["placeholder_form_submit"] if page.placeholder_forms else [])
                + (["placeholder_cta_href"] if placeholder_links else [])
                + (["self_referential_cta_href"] if self_links else [])
            )
            results.append({
                "path": str(path.relative_to(root)), "title": page.title_text,
                "has_description": bool(page.description), "h1_count": page.headings,
                "forms": page.forms, "placeholder_forms": page.placeholder_forms,
                "placeholder_cta_links": placeholder_links,
                "self_referential_cta_links": self_links,
                "cta_links": ctas, "warnings": warnings,
            })
        except (UnicodeError, ValueError) as e:
            results.append({"path": str(path.relative_to(root)), "error": str(e)})
    return results

if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    print(json.dumps({"audit_type": "static_only", "pages": audit(root)}, ensure_ascii=False, indent=2))
