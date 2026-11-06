#!/usr/bin/env python3
"""Read-only static conversion audit for Sustainashield HTML pages.
No credentials, network requests, analytics claims, or production changes.
"""
from pathlib import Path
from html.parser import HTMLParser
import json
import sys

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = False
        self.title_text = ""
        self.links = []
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
        if tag == "a": self.links.append({"href": a.get("href", ""), "text": ""})
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

    def handle_data(self, data):
        if self.title: self.title_text += data.strip()
        if self.links: self.links[-1]["text"] += data.strip()

def audit(root):
    results = []
    for path in sorted(root.rglob("*.html")):
        if ".git" in path.parts: continue
        page = Page()
        try:
            page.feed(path.read_text(encoding="utf-8"))
            ctas = [x for x in page.links if x["href"].startswith(("tel:", "mailto:", "https://line.me/", "https://lin.ee/")) or any(w in x["text"] for w in ("相談", "問い合わせ", "見積"))]
            results.append({"path": str(path.relative_to(root)), "title": page.title_text, "has_description": bool(page.description), "h1_count": page.headings, "forms": page.forms, "placeholder_forms": page.placeholder_forms, "cta_links": ctas, "warnings": (["no_title"] if not page.title_text else []) + (["no_meta_description"] if not page.description else []) + (["no_h1"] if not page.headings else []) + (["no_obvious_cta"] if not ctas and not page.forms else []) + (["placeholder_form_submit"] if page.placeholder_forms else [])})
        except (UnicodeError, ValueError) as e:
            results.append({"path": str(path.relative_to(root)), "error": str(e)})
    return results

if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    print(json.dumps({"audit_type": "static_only", "pages": audit(root)}, ensure_ascii=False, indent=2))
