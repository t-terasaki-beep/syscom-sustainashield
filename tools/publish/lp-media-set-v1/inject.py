#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LP共通「資料・動画セット」v1 を、本番ミラー（お名前.com から取得した public_html の写し）の各LPへ差し込む。

  python3 inject.py --site <本番ミラー> --out <公開物フォルダ>            # DryRun（差分と一覧だけ作る）
  python3 inject.py --site <本番ミラー> --out <公開物フォルダ> --apply    # 公開物フォルダに差し込み済みHTMLを書き出す

・本番ミラーは書き換えない。変更したファイルだけを --out に同じパスで書き出す（そのままFTPで上げられる形）
・ページ→動画・資料の割り当ては media-map.json（URL前方一致・長い方が優先）
・<!-- ss-media-set:v1 --> 〜 <!-- /ss-media-set:v1 --> で囲むので、再実行すると置き換わる（二重にならない）
・noindex のページ、除外パス（提案書・研究会・フォーム等）には入れない
・/download/ が本番ミラーに無ければ、復旧用ページを --out/download/index.html に出して警告する
  （本番にあっても --replace-download でキット版＝スケッチ資料の選択肢入りに置き換えられる）
・出力：--out/_report/changes.csv（ページ・テーマ・動画・資料・挿入位置）、SHA256SUMS.txt
"""
import argparse, csv, hashlib, html, json, os, re, shutil, sys

KIT = os.path.dirname(os.path.abspath(__file__))
MARK_BEGIN, MARK_END = "<!-- ss-media-set:v1 -->", "<!-- /ss-media-set:v1 -->"
CSS_TAG = '<link rel="stylesheet" href="/assets/ss-media-set-v1.css?v=1">'
JS_TAG = '<script src="/assets/ss-media-set-v1.js?v=1" defer></script>'
DOC_ICON = ('<svg viewBox="0 0 40 48" aria-hidden="true"><path d="M4 0h22l14 14v30a4 4 0 0 1-4 4H4a4 4 0 0 1-4-4V4a4 4 0 0 1 4-4z" fill="#E8F7FD"/>'
            '<path d="M26 0v10a4 4 0 0 0 4 4h10" fill="#B9D3DF"/><text x="20" y="36" text-anchor="middle" font-size="11" font-weight="700" '
            'font-family="Montserrat,sans-serif" fill="#0093CF">PDF</text></svg>')


def load_map():
    with open(os.path.join(KIT, "media-map.json"), encoding="utf-8") as f:
        return json.load(f)


def url_of(site, path):
    rel = os.path.relpath(path, site).replace(os.sep, "/")
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def theme_for(url, m):
    best = ""
    for prefix in m["routes"]:
        if url.startswith(prefix) and len(prefix) > len(best):
            best = prefix
    return m["routes"].get(best, "default")


def excluded(url, m):
    return any(url.startswith(p) or url.rstrip("/") == p.rstrip("/") for p in m["exclude"])


def is_noindex(src):
    return re.search(r'<meta[^>]+name=["\']robots["\'][^>]+noindex', src, re.I) is not None


def block_html(url, theme_key, m):
    t = m["themes"][theme_key]
    dl = m["download_page"]
    cards = []
    for vid in t["videos"][:2]:
        v = m["videos"][vid]
        title = html.escape(v["title"])
        cards.append(
            '<div class="ssm-card"><span class="ssm-tag">YouTube</span>'
            '<h3>%s</h3><p>%s</p>'
            '<button type="button" class="ssm-yt" data-yt="%s" aria-label="%s を再生">'
            '<img src="https://i.ytimg.com/vi/%s/hqdefault.jpg" alt="" loading="lazy" width="480" height="360"></button></div>'
            % (title, html.escape(v["note"]), vid, title, vid))
    docs = []
    for key in t["docs"]:
        d = m["docs"][key]
        is_sketch = d.get("sketch")
        href = "%s?doc=%s&amp;from=%s" % (dl, key, html.escape(url, quote=True))
        docs.append(
            '<a class="ssm-doc" href="%s" data-ssm-doc="%s" data-event="cta_click">%s<span><b>%s</b><small>%s</small></span></a>'
            % (href, key, DOC_ICON, html.escape(d["title"]),
               ("メーカー：%s｜フォームからお送りします" % html.escape(d["maker"])) if is_sketch else "フォームからお送りします"))
    tag = '<span class="ssm-tag is-sketch">スケッチ商材資料</span>' if any(m["docs"][k].get("sketch") for k in t["docs"]) else '<span class="ssm-tag">資料</span>'
    doc_card = (
        '<div class="ssm-card">%s<h3>資料をダウンロード</h3>'
        '<p>仕組み・施工の流れ・確認することを、印刷して社内やご家族と共有できる形でお送りします。</p>%s'
        '<a class="ssm-btn" href="%s?from=%s" data-ssm-doc="download-page" data-event="cta_click">資料ダウンロードへ</a></div>'
        % (tag, "".join(docs), dl, html.escape(url, quote=True)))
    return (
        '%s\n<section class="ssm" id="ssm-media" aria-labelledby="ssm-h">'
        '<div class="ssm-wrap"><span class="ssm-en">Movie &amp; Document</span>'
        '<h2 class="ssm-h2" id="ssm-h">%sを 動画と資料で確かめる</h2>'
        '<p class="ssm-lead">文章だけでは伝わりにくいところを、TERAちゃんねるの解説動画と資料で補います。</p>'
        '<div class="ssm-grid">%s%s</div>'
        '<a class="ssm-more" href="/videos/">テーマ別の解説動画をすべて見る</a><a class="ssm-more" style="margin-top:8px" href="/column/">寺嵜のコラムを読む</a>'
        '</div></section>\n%s'
        % (MARK_BEGIN, html.escape(t["label"]), "".join(cards), doc_card, MARK_END))


def insert(src, block):
    # 既存ブロックは置き換え
    pat = re.compile(re.escape(MARK_BEGIN) + r".*?" + re.escape(MARK_END), re.S)
    if pat.search(src):
        return pat.sub(lambda _: block, src, count=1), "replace"
    body = src.lower()
    # サイト共通フッターはページ末尾側にあるので、最後の <footer の直前に入れる（記事内の <footer> を避ける）
    for needle, where in (("<footer", "before-footer"), ("</main>", "before-main-end"), ("</body>", "before-body-end")):
        i = body.rfind(needle)
        if i > 0:
            return src[:i] + block + "\n" + src[i:], where
    return None, "no-anchor"


def add_assets(src):
    if "ss-media-set-v1.css" not in src:
        i = src.lower().find("</head>")
        if i < 0:
            return None
        src = src[:i] + CSS_TAG + "\n" + src[i:]
    if "ss-media-set-v1.js" not in src:
        i = src.lower().rfind("</body>")
        if i < 0:
            return None
        src = src[:i] + JS_TAG + "\n" + src[i:]
    return src


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--replace-download", action="store_true", help="本番の /download/ をキット版（スケッチ資料の選択肢入り）に置き換える")
    a = ap.parse_args()
    m = load_map()
    site, out = os.path.abspath(a.site), os.path.abspath(a.out)
    if out.startswith(site + os.sep) or out == site:
        sys.exit("ERROR: --out を本番ミラーの中に置かないでください")
    os.makedirs(os.path.join(out, "_report"), exist_ok=True)
    rows, written = [], []
    for dirpath, dirs, files in os.walk(site):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        for fn in sorted(files):
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            url = url_of(site, path)
            with open(path, encoding="utf-8", errors="surrogateescape") as f:
                src = f.read()
            if excluded(url, m):
                rows.append([url, "", "", "", "skip:excluded"]); continue
            if is_noindex(src):
                rows.append([url, "", "", "", "skip:noindex"]); continue
            theme = theme_for(url, m)
            new, where = insert(src, block_html(url, theme, m))
            if new is None:
                rows.append([url, theme, "", "", "skip:" + where]); continue
            new = add_assets(new)
            if new is None:
                rows.append([url, theme, "", "", "skip:no-head-or-body"]); continue
            t = m["themes"][theme]
            rows.append([url, theme, " ".join(t["videos"][:2]), " ".join(t["docs"]), where])
            if a.apply and new != src:
                dst = os.path.join(out, os.path.relpath(path, site))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(dst, "w", encoding="utf-8", errors="surrogateescape", newline="") as f:
                    f.write(new)
                written.append(dst)
    # 共通ファイル
    extras = [("assets/ss-media-set-v1.css", "assets/ss-media-set-v1.css"),
              ("assets/ss-media-set-v1.js", "assets/ss-media-set-v1.js"),
              ("videos/index.html", "videos/index.html"),
              ("column/index.html", "column/index.html")]
    dl_exists = os.path.exists(os.path.join(site, "download", "index.html"))
    if not dl_exists or a.replace_download:
        extras.append(("download/index.html", "download/index.html"))
        print("WARN: 本番ミラーに /download/ がありません → 復旧用ページを出力します")
    if a.apply:
        for src_rel, dst_rel in extras:
            dst = os.path.join(out, dst_rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(os.path.join(KIT, src_rel), dst)
            written.append(dst)
    with open(os.path.join(out, "_report", "changes.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["url", "theme", "videos", "docs", "result"])
        w.writerows(rows)
    if a.apply:
        with open(os.path.join(out, "_report", "SHA256SUMS.txt"), "w", encoding="utf-8") as f:
            for p in written:
                f.write("%s  %s\n" % (sha(p), os.path.relpath(p, out).replace(os.sep, "/")))
    done = sum(1 for r in rows if not r[4].startswith("skip"))
    print("pages=%d inserted=%d skipped=%d download_page=%s mode=%s"
          % (len(rows), done, len(rows) - done, "OK" if dl_exists else "MISSING", "apply" if a.apply else "dry-run"))


if __name__ == "__main__":
    main()
