#!/usr/bin/env python3
"""Read-only static conversion audit for Sustainashield HTML pages.
No credentials, network requests, analytics claims, or production changes.
"""
from pathlib import Path
import posixpath
from html.parser import HTMLParser
import json
import sys
from urllib.parse import urlsplit, urljoin

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
    """Flag same-document inquiry CTA links, including live absolute and directory URLs.

    Static heuristic only: a fragment or reload is not an alternative contact
    endpoint. Unrelated domains, tel/mailto, and cross-page links are preserved.
    """
    href = (link["href"] or "").strip()
    if not any(word in link["text"] for word in ("相談", "問い合わせ", "見積")):
        return False
    if not href or is_placeholder_cta_href(link):
        return False

    try:
        parsed = urlsplit(href)
        if parsed.scheme or parsed.netloc:
            if parsed.scheme not in ("", "http", "https"):
                return False
            if parsed.hostname not in (
                "syscom-sustaina-shield.com", "www.syscom-sustaina-shield.com"
            ):
                return False
            route = parsed.path or "/"
        else:
            route = parsed.path
    except ValueError:
        return False

    # "#consult" and "?source=..." revisit this document; they do not
    # become independent consultation destinations by having a fragment/query.
    if not route:
        return bool(parsed.query or parsed.fragment)

    def document_path(path):
        # On GitHub, /residential/ is residential/index.html, not residential.
        return posixpath.normpath((path.lstrip("/") + "index.html")
                                 if path.endswith("/") else path.lstrip("/"))

    target = (document_path(route) if route.startswith("/")
              else document_path(posixpath.join(posixpath.dirname(page_path), route)))
    return target == document_path(page_path)


def diagnosis_reference_target(href, page_path):
    """Classify only exact same-site photo diagnosis aliases in a static source tree.

    This does NOT prove the published site uses the same links or whether an
    HTTP redirect/canonical tag exists. Keep both URLs unchanged.
    """
    href = (href or "").strip()
    if not href or href.startswith(("#", "?")):
        return None
    try:
        u = urlsplit(urljoin("https://syscom-sustaina-shield.com/" + page_path, href))
    except ValueError:
        return None
    if u.scheme not in ("http", "https") or u.hostname not in (
        "syscom-sustaina-shield.com", "www.syscom-sustaina-shield.com"
    ):
        return None
    route = posixpath.normpath(u.path)
    if route in ("/photo-diagnosis", "/photo-diagnosis/index.html"):
        return "/photo-diagnosis/"
    if route == "/shindan.html":
        return "/shindan.html"
    return None


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
            diagnosis_links = [
                {"target": target, "href": link["href"], "text": link["text"]}
                for link in page.links
                if (target := diagnosis_reference_target(link["href"], page_path)) is not None
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
                "cta_links": ctas, "diagnosis_links": diagnosis_links, "warnings": warnings,
            })
        except (UnicodeError, ValueError) as e:
            results.append({"path": str(path.relative_to(root)), "error": str(e)})
    return results

if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    print(json.dumps({"audit_type": "static_only", "pages": audit(root)}, ensure_ascii=False, indent=2))
