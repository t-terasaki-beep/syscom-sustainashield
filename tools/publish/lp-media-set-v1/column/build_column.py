#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
コラム一覧 /column/ と記事ページ /column/<slug>/ を articles.json から生成する。

  python3 build_column.py

・source=site の記事は本文ページを生成（Notion 📝 note記事DB の「note本文開始〜終了」を転記したもの）
・source=note の記事は一覧カードから note へリンク（サイト内に本文を複製しない）
・並び順は日付の新しい順。同じ日付は articles.json の順
"""
import html, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = "https://syscom-sustaina-shield.com"
CATS = [("all", "すべて", ""), ("solar", "太陽光・蓄電池", "#F59E0B"), ("ecocute", "エコキュート・給湯", "#EF5B5B"),
        ("energy", "省エネ・電気代", "#16A34A"), ("home", "住まいを守る", "#0D9488"), ("subsidy", "補助金・制度", "#8B5CF6"),
        ("biz", "法人・事業者向け", "#2563EB"), ("local", "地域・コラム", "#0EA5E9"), ("news", "お知らせ", "#64748B")]
CM = {k: (n, c) for k, n, c in CATS}
ICON = {"solar": "M12 3v2M12 19v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M3 12h2M19 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4M12 8a4 4 0 100 8 4 4 0 000-8z",
        "ecocute": "M7 3h10v18H7zM10 7h4M10 11h4", "energy": "M13 2L4 14h7l-1 8 9-12h-7z", "home": "M3 11l9-7 9 7v9H3zM9 20v-6h6v6",
        "subsidy": "M5 4h14v16H5zM9 8h6M9 12h6M9 16h3", "biz": "M3 21V8l6-4v17M9 21h12V11l-6-3M13 13h2M13 17h2",
        "local": "M12 21s7-6 7-11a7 7 0 10-14 0c0 5 7 11 7 11zM12 8a2 2 0 100 4 2 2 0 000-4z", "news": "M4 5h16v11H8l-4 4z"}
LINE = {"home": ("https://line.me/R/ti/p/%40631cqlgf", "住まいのLINEで相談する"),
        "biz": ("https://line.me/R/ti/p/%40119upwsl", "法人・事業のLINEで相談する")}
LEAF = '<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M34 4C16 4 6 14 6 28c0 3 1 5 2 7 3-11 10-18 20-23-8 6-14 13-17 23 16 2 26-10 23-31z" fill="#16A34A"/></svg>'
E = html.escape


def ic(k):
    p = ICON.get(k)
    return f'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="{p}"/></svg>' if p else ""


def head(title, desc, canon, depth):
    up = "../" * depth
    return f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{SITE}{canon}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{SITE}{canon}"><meta property="og:type" content="{'article' if depth else 'website'}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&family=Dancing+Script:wght@600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/column/column.css?v=2">
</head><body>
<header class="cl-hd"><div class="cl-wrap">
<a class="cl-logo" href="/">{LEAF}<span>サステナシールド<small>SUSTAINA SHIELD</small></span></a>
<nav class="cl-nav" aria-label="メインメニュー"><a href="/">ホーム</a><a href="/business/">法人のお客様</a><a href="/residential/">住宅のお客様</a><a href="/service.html">製品・サービス</a><a href="/hojokin/">補助金・制度</a><a href="/videos/">解説動画</a><a href="/column/" aria-current="page">コラム</a><a href="/company.html">会社案内</a></nav>
<div class="cl-btns"><a class="cl-btn" href="/contact.html">お問い合わせ</a><a class="cl-btn line" href="https://line.me/R/ti/p/%40631cqlgf" data-event="line_click">LINEで相談</a></div>
</div></header>
'''


FOOT = '''<footer class="cl-ft"><div class="cl-wrap">© シスコムサステナシールド｜<a href="/privacy.html">プライバシーポリシー</a>｜<a href="/column/">コラム</a>｜<a href="/videos/">解説動画</a>｜<a href="/download/">資料ダウンロード</a></div></footer>
'''


def card(a, depth=0):
    ext = a["source"] == "note"
    tgt = ' target="_blank" rel="noopener"' if ext else ""
    n, c = CM[a["cat"]]
    via = "note" if ext else "サイト"
    return (f'<article class="cl-card" data-cat="{a["cat"]}" data-q="{E(a["title"] + a["summary"])}">'
            f'<a href="{a["url"]}"{tgt} data-event="cta_click" data-cta-type="column_{via}">'
            f'<div class="cl-img"><img src="/column/img/{a["img"]}.jpg" alt="" loading="lazy" width="640" height="360"></div>'
            f'<div class="cl-body"><div class="cl-meta"><span class="cl-tag" style="--c:{c}">{ic(a["cat"])}{n}</span><time>{a["date"]}</time></div>'
            f'<h2>{E(a["title"])}</h2><p>{E(a["summary"])}</p><span class="cl-go" aria-hidden="true">›</span></div></a></article>')


def body_html(text):
    out = []
    for para in re.split(r"\n\s*\n", text.strip()):
        para = para.strip()
        if not para:
            continue
        if para.startswith("■"):
            out.append(f"<h2>{E(para.lstrip('■ ').strip())}</h2>")
            continue
        lines = []
        for ln in para.split("\n"):
            ln = E(ln.strip())
            ln = re.sub(r"(https?://[^\s<]+)", r'<a href="\1" target="_blank" rel="noopener">\1</a>', ln)
            lines.append(ln)
        out.append("<p>" + "<br>".join(lines) + "</p>")
    return "\n".join(out)


def build():
    data = json.load(open(os.path.join(HERE, "articles.json"), encoding="utf-8"))
    arts = sorted(data["articles"], key=lambda a: a["date"], reverse=True)  # 安定ソート
    # 一覧
    chips = "".join(f'<button type="button" class="cl-chip{" is-on" if k == "all" else ""}" data-cat="{k}">{ic(k)}{n}</button>' for k, n, _ in CATS)
    side = "".join(f'<li><a href="{a["url"]}"{" target=_blank rel=noopener" if a["source"] == "note" else ""}><b>{i + 1}</b>'
                   f'<img src="/column/img/{a["img"]}.jpg" alt="" loading="lazy" width="96" height="64"><span>{E(a["title"])}</span></a></li>'
                   for i, a in enumerate(arts[:5]))
    idx = head("サステナシールド コラム｜エネルギー・住まい・地域のこれから",
               "太陽光・蓄電池、エコキュート、省エネ、停電対策、補助金、法人の設備投資まで。現場で聞かれたことを、寺嵜がわかりやすくまとめたコラムです。",
               "/column/", 0)
    idx += f'''<section class="cl-hero"><div class="cl-wrap">
<p class="pre">未来の暮らしとビジネスのヒントが見つかる</p>
<h1><span class="nb">サステナシールド</span> <span class="nb">コラム</span></h1>
<p class="sub">エネルギー・住まい・地域のこれからを、わかりやすく。</p>
<p class="script" aria-hidden="true">For a Sustainable<br>&nbsp;&nbsp;&nbsp;&nbsp;Future</p>
<svg class="leaf" viewBox="0 0 200 200" aria-hidden="true"><path d="M100 196V120" stroke="#3E7D3A" stroke-width="5" fill="none"/><path d="M100 128C60 128 30 100 26 58c40 2 70 26 74 70z" fill="#6DBE45"/><path d="M100 118c8-50 42-84 90-92-4 52-38 86-90 92z" fill="#8FD14F"/><path d="M100 118c20-30 45-55 80-80M100 128C80 104 58 86 34 66" stroke="#fff" stroke-opacity=".5" stroke-width="2" fill="none"/></svg>
<p class="msg">今日の気づきが<br>明日の持続可能な<br>社会につながる。</p>
</div></section>
<div class="cl-wrap">
<div class="cl-chips" role="tablist" aria-label="カテゴリ">{chips}</div>
<div class="cl-main">
<div><div class="cl-grid" id="cl-grid">{"".join(card(a) for a in arts)}<p class="cl-empty" hidden>このカテゴリの記事は準備中です。気になることは<a href="/contact.html" style="text-decoration:underline">お問い合わせ</a>・LINEからどうぞ。</p></div>
<p class="cl-note">一部の記事は note（<a href="https://note.com/syscom_sustaina" target="_blank" rel="noopener" style="text-decoration:underline">syscom_sustaina</a>）で公開しています。写真はイメージです。</p></div>
<aside class="cl-side">
<form class="cl-search" role="search" onsubmit="return false"><input id="cl-q" type="search" placeholder="コラムを検索..." aria-label="コラムを検索"><button type="submit" aria-label="検索"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg></button></form>
<div class="cl-box"><h3><svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 8l4 4 5-7 5 7 4-4-2 11H5z" fill="#F5A623"/></svg>新着の記事</h3><ol class="cl-rank">{side}</ol></div>
<div class="cl-cta"><h3>{LEAF.replace('viewBox', 'width="26" height="26" viewBox', 1)}お困りごとはありませんか？</h3>
<p>住まい・法人のエネルギー、補助金のご相談など、お気軽にお問い合わせください。</p>
<a href="/contact.html" data-event="cta_click">無料で相談する <span aria-hidden="true">›</span></a>
<a class="sub2" href="/download/?from=/column/" data-event="cta_click">資料をダウンロード</a></div>
</aside></div></div>
{FOOT}<script>
(function(){{var cat='all',q='';var cards=[].slice.call(document.querySelectorAll('.cl-card')),empty=document.querySelector('.cl-empty');
function run(){{var n=0;cards.forEach(function(c){{var ok=(cat==='all'||c.dataset.cat===cat)&&(!q||c.dataset.q.indexOf(q)>=0);c.hidden=!ok;if(ok)n++;}});empty.hidden=n>0;}}
document.querySelectorAll('.cl-chip').forEach(function(b){{b.addEventListener('click',function(){{document.querySelectorAll('.cl-chip').forEach(function(x){{x.classList.remove('is-on');x.setAttribute('aria-selected','false')}});b.classList.add('is-on');b.setAttribute('aria-selected','true');cat=b.dataset.cat;run();}});}});
document.getElementById('cl-q').addEventListener('input',function(e){{q=e.target.value.trim();run();}});}})();
</script>
</body></html>
'''
    open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(idx)
    # 記事ページ
    n = 0
    for a in arts:
        if a["source"] != "site":
            continue
        cname, ccol = CM[a["cat"]]
        rel = [b for b in arts if b is not a and b["cat"] == a["cat"]][:3]
        rel += [b for b in arts if b is not a and b not in rel][: 3 - len(rel)]
        lurl, llabel = LINE[a["audience"]]
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": a["title"], "description": a["summary"],
              "datePublished": a["date"].replace(".", "-"), "author": {"@type": "Person", "name": "寺嵜忠弘"},
              "publisher": {"@type": "Organization", "name": "シスコムサステナシールド"},
              "image": f'{SITE}/column/img/{a["img"]}.jpg', "mainEntityOfPage": f'{SITE}{a["url"]}'}
        pg = head(f'{a["title"]}｜サステナシールド コラム', a["summary"], a["url"], 2)
        pg += f'''<main class="ca-wrap">
<nav class="ca-crumb" aria-label="パンくず"><a href="/">ホーム</a> / <a href="/column/">コラム</a> / {E(cname)}</nav>
<div class="ca-hero"><img src="/column/img/{a["img"]}.jpg" alt="" width="1200" height="600"></div>
<div class="ca-head"><div class="cl-meta"><span class="cl-tag" style="--c:{ccol}">{ic(a["cat"])}{cname}</span><time datetime="{a["date"].replace(".", "-")}">{a["date"]}</time></div>
<h1>{E(a["title"])}</h1></div>
<div class="ca-body">
{body_html(a["body"])}
</div>
<div class="ca-cta"><p>読んで気になったところがあれば、今分かっていることから一緒に整理します。</p>
<div class="row"><a class="line" href="{lurl}" data-event="line_click">{llabel}</a><a href="{a["lp"]}" data-event="cta_click">関連する相談ページを見る</a><a class="ghost" href="/download/?from={a["url"]}" data-event="cta_click">資料をダウンロード</a></div></div>
<section class="ca-rel"><h2>あわせて読みたい</h2><div class="cl-grid">{"".join(card(b) for b in rel)}</div></section>
<p class="ca-note">写真はイメージです。記事内の会話は、説明のための例えの場面です。</p>
</main>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
{FOOT}</body></html>
'''
        d = os.path.join(HERE, a["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(pg)
        n += 1
    print("index + %d articles" % n)


if __name__ == "__main__":
    build()
