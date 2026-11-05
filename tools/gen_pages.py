# -*- coding: utf-8 -*-
"""課題LP・住宅HUB ジェネレーター（P0-2 / P0-3 / P0-4）
実行: python3 tools/gen_pages.py <repo_root>  （課題LP6ページ＋住宅HUBを再生成する。文言・構成はこのファイルが正本）
"""
import sys, os, json, html

ROOT = sys.argv[1]
SITE = "https://syscom-sustaina-shield.com"
FORMS = "https://forms.gle/3u6ep7TNp73fqY728"
TEL = "tel:+81-90-9326-4456"
TEL_DISP = "090-9326-4456"
LINE_B = "https://page.line.me/119upwsl"          # 法人 @119upwsl
LINE_R = "https://line.me/R/ti/p/@631cqlgf"       # 住宅総合 @631cqlgf
LINE_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M19.365 9.863c.349 0 .63.285.63.631 0 .345-.281.63-.63.63H17.61v1.125h1.755c.349 0 .63.283.63.63 0 .344-.281.629-.63.629h-2.386c-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.63-.63h2.386c.346 0 .627.285.627.63 0 .349-.281.63-.63.63H17.61v1.125h1.755zm-3.855 3.016c0 .27-.174.51-.432.596-.064.021-.133.031-.199.031-.211 0-.391-.09-.51-.25l-2.443-3.317v2.94c0 .344-.279.629-.631.629-.346 0-.626-.285-.626-.629V8.108c0-.27.173-.51.43-.595.06-.023.136-.033.194-.033.195 0 .375.104.495.254l2.462 3.33V8.108c0-.345.282-.63.63-.63.345 0 .63.285.63.63v4.771zm-5.741 0c0 .344-.282.629-.631.629-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.63-.63.346 0 .628.285.628.63v4.771zm-2.466.629H4.917c-.345 0-.63-.285-.63-.629V8.108c0-.345.285-.63.63-.63.348 0 .63.285.63.63v4.141h1.756c.348 0 .629.283.629.63 0 .344-.282.629-.629.629M24 10.314C24 4.943 18.615.572 12 .572S0 4.943 0 10.314c0 4.811 4.27 8.842 10.035 9.608.391.082.923.258 1.058.59.12.301.079.766.038 1.08l-.164 1.02c-.045.301-.24 1.186 1.049.645 1.291-.539 6.916-4.078 9.436-6.975C23.176 14.393 24 12.458 24 10.314"/></svg>'

# 書体（2026-09-26 方針：Noto Sans JP 本文400・見出し700 ＋ Montserrat 英字ラベル・番号）
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Montserrat:wght@600;700&display=swap" rel="stylesheet">'

# セクション見出しの上に置く英字ラベル（id → ラベル）。見出しの型＝英字ラベル → 日本語見出し → 短罫
EN_LABELS = {
    "anata": "YOUR CASE", "komarigoto": "YOUR CASE", "scene": "SCENE", "genin": "CAUSE", "kakunin": "CHECK",
    "paths": "SOLUTIONS", "hiyou": "COST", "trust": "OUR PROMISE", "faq": "FAQ", "next": "NEXT STEP",
    "related": "RELATED", "soudan-hub": "CONSULT", "direct": "DIRECT",
}
import re as _re
def add_en_labels(out):
    def rep(m):
        label = EN_LABELS.get(m.group(2))
        if not label:
            return m.group(0)
        return f'{m.group(1)}<div class="en">{label}</div>\n    <h2 class="h2">'
    return _re.sub(r'(<section class="[^"]*" id="([^"]+)">\s*<div class="wrap">\s*)<h2 class="h2">', rep, out)

MENU_SVG_TEL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/></svg>'
MAIL_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>'

DRAWER_JS = '''<script>
(function(){var b=document.body,btn=document.querySelector('.menu-btn'),bg=document.querySelector('.drawer-bg');if(!btn)return;
function t(o){b.classList.toggle('is-drawer',o);btn.setAttribute('aria-expanded',o?'true':'false')}
btn.addEventListener('click',function(){t(!b.classList.contains('is-drawer'))});
if(bg)bg.addEventListener('click',function(){t(false)});
document.querySelectorAll('.drawer a').forEach(function(a){a.addEventListener('click',function(){t(false)})});
document.addEventListener('keydown',function(e){if(e.key==='Escape')t(false)});})();
</script>'''

# ---- ヒーロー写真（2026-09-27）------------------------------------------
# 本番サイトに掲載済みの写真を流用（寺嵜指示）。足りない枠は生成画像で補う。
# どちらも実際の施工・測定の写真ではないため、キャプション先頭に「写真はイメージです」を必ず付ける。
# 写真が未配置の枠は従来のプレースホルダーを出す。
HERO_PHOTOS = {
    # file: (assets/photos/ のファイル名, object-position)
    "business/atsui/index.html":     ("warehouse-roof.jpg", "center 40%"),
    "business/denkidai/index.html":  ("office-demand.jpg", "center"),
    "business/cubicle/index.html":   ("cubicle-check.jpg", "center"),
    "residential/index.html":        ("home-family.jpg", "60% center"),
    "residential/ecocute/index.html": ("ecocute-consult.jpg", "45% center"),
    "residential/solar/index.html":  ("home-solar.jpg", "center"),
    "residential/battery/index.html": ("home-battery.jpg", "58% center"),
}
IMAGE_NOTE = "写真はイメージです。"

def hero_figure(file, rel, alt, caption):
    ph = HERO_PHOTOS.get(file)
    if ph and os.path.exists(os.path.join(ROOT, "assets", "photos", ph[0])):
        return (f'<figure class="hero-photo has-img"><img src="{rel}assets/photos/{ph[0]}" alt="{esc(alt.replace("の実写", ""))}（イメージ）" '
                f'width="1200" height="750" loading="eager" decoding="async" style="object-position:{ph[1]}"></figure>\n'
                f'      <div class="hero-caption">{esc(IMAGE_NOTE + caption.removeprefix("写真1 "))}</div>')
    return (f'<figure class="hero-photo" aria-label="{esc(alt)}">\n'
            f'        <div class="ph"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="12" cy="12" r="3.5"/><path d="M7 5l1.5-2h7L17 5"/></svg><span>{esc(alt)}</span><span style="font-size:12px;color:var(--muted)">写真を準備中</span></div>\n'
            f'      </figure>\n'
            f'      <div class="hero-caption">{esc(caption)}</div>')

def esc(s):
    return html.escape(s, quote=True)

def head(p):
    faq_ld = ""
    if p.get("faq"):
        faq_ld = json.dumps({
            "@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]
        }, ensure_ascii=False)
        faq_ld = f'<script type="application/ld+json">{faq_ld}</script>'
    crumbs = [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(p["crumbs"])]
    bc_ld = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": crumbs}, ensure_ascii=False)
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(p["title"])}</title>
<meta name="description" content="{esc(p["desc"])}">
<link rel="canonical" href="{SITE}{p["path"]}">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(p["og_title"])}">
<meta property="og:description" content="{esc(p["desc"])}">
<meta property="og:url" content="{SITE}{p["path"]}">
<meta name="robots" content="index,follow">
{FONTS}
<link rel="stylesheet" href="{p["rel"]}assets/kadai.css">
<script type="application/ld+json">{bc_ld}</script>
{faq_ld}
</head>
<body>
'''

def header(p):
    rel = p["rel"]
    if p["audience"] == "business":
        top = f'<span>京葉工業地域から、明日の千葉をつくる ｜ シスコムサステナシールド</span><span><a href="{rel}residential/">ご家庭の方はこちら</a> ｜ <a href="{rel}faq.html">よくあるご質問</a></span>'
        nav = f'''<a href="{rel}#komarigoto">困りごとから探す</a>
      <a href="{rel}#services">サービス</a>
      <a href="{rel}company.html">会社案内</a>
      <a href="{rel}simulator/">シミュレーター</a>
      <a href="{FORMS}" target="_blank" rel="noopener" class="cta-mini">無料診断</a>'''
    else:
        top = f'<span>千葉のご家庭の 暑さ寒さ・電気代・設備・停電の相談窓口 ｜ シスコムサステナシールド</span><span><a href="{rel}">法人の方はこちら</a> ｜ <a href="{rel}faq.html">よくあるご質問</a></span>'
        nav = f'''<a href="{rel}residential/#komarigoto">困りごとから探す</a>
      <a href="{rel}service.html">給湯器・エコキュート</a>
      <a href="{rel}sotsu-fit/">卒FIT</a>
      <a href="{rel}company.html">会社案内</a>
      <a href="{rel}contact.html" class="cta-mini">相談する</a>'''
    crumb = ' '.join(
        (f'<a href="{rel}{u.lstrip("/")}">{esc(n)}</a>' if i == 0 else f'<span><a href="{rel}{u.lstrip("/")}">{esc(n)}</a></span>') if i < len(p["crumbs"]) - 1 else f'<span>{esc(n)}</span>'
        for i, (n, u) in enumerate(p["crumbs"]))
    # スマホ用ドロワー（ハンバーガー）：見出し → リンク → 電話 → 相談ボタン
    if p["audience"] == "business":
        drawer = f'''<div><div class="d-title">法人の困りごと</div><ul>
        <li><a href="{rel}#komarigoto">困りごとから探す</a></li>
        <li><a href="{rel}business/atsui/">工場・倉庫が暑い</a></li>
        <li><a href="{rel}business/denkidai/">電気代・デマンドが高い</a></li>
        <li><a href="{rel}business/cubicle/">キュービクルの更新</a></li>
        <li><a href="{rel}shanetsu-chiba/">千葉の遮熱（専門ページ）</a></li>
      </ul></div>
      <div><div class="d-title">会社情報</div><ul>
        <li><a href="{rel}company.html">会社案内</a></li>
        <li><a href="{rel}faq.html">よくあるご質問</a></li>
        <li><a href="{rel}residential/">ご家庭の方はこちら</a></li>
      </ul></div>
      <a class="d-tel" href="{TEL}">{TEL_DISP}<small>9:00〜18:00 お電話でも承ります</small></a>
      <a class="btn btn-gold" href="{FORMS}" target="_blank" rel="noopener" data-event="cta_click" data-cta-type="drawer_consult" data-cta-position="drawer">無料診断・相談する</a>'''
    else:
        drawer = f'''<div><div class="d-title">住まいの困りごと</div><ul>
        <li><a href="{rel}residential/#komarigoto">困りごとから探す</a></li>
        <li><a href="{rel}residential/ecocute/">エコキュートの交換・故障</a></li>
        <li><a href="{rel}residential/solar/">太陽光は元が取れるか</a></li>
        <li><a href="{rel}residential/battery/">蓄電池は必要か・停電で何時間</a></li>
        <li><a href="{rel}sotsu-fit/">卒FIT後どうするか</a></li>
      </ul></div>
      <div><div class="d-title">サービス・会社情報</div><ul>
        <li><a href="{rel}service.html">給湯器・エコキュート</a></li>
        <li><a href="{rel}company.html">会社案内</a></li>
        <li><a href="{rel}faq.html">よくあるご質問</a></li>
        <li><a href="{rel}">法人の方はこちら</a></li>
      </ul></div>
      <a class="d-tel" href="{TEL}">{TEL_DISP}<small>9:00〜18:00 お電話でも承ります</small></a>
      <a class="btn btn-gold" href="{rel}contact.html" data-event="cta_click" data-cta-type="drawer_consult" data-cta-position="drawer">相談する</a>'''
    return f'''<div class="topbar"><div class="topbar-inner">{top}</div></div>
<header class="site-header">
  <div class="header-inner">
    <a href="{rel}" class="brand">
      <div class="brand-mark">S</div>
      <div class="brand-text"><div class="name">シスコムサステナシールド</div><div class="sub">SYSCOM SUSTAINA SHIELD</div></div>
    </a>
    <nav class="gnav">
      {nav}
    </nav>
    <button class="menu-btn" type="button" aria-label="メニューを開く" aria-expanded="false" aria-controls="drawer"><span></span><span></span><span></span></button>
  </div>
</header>
<div class="drawer-bg" aria-hidden="true"></div>
<nav class="drawer" id="drawer" aria-label="メニュー">
      {drawer}
</nav>
<div class="crumb" aria-label="パンくず">{crumb}</div>
'''

def footer(p):
    rel = p["rel"]
    if p["audience"] == "business":
        col1 = f'''<h4>法人の困りごと</h4><ul>
          <li><a href="{rel}#komarigoto">困りごとから探す（法人）</a></li>
          <li><a href="{rel}business/atsui/">工場・倉庫が暑い</a></li>
          <li><a href="{rel}business/denkidai/">電気代・デマンドが高い</a></li>
          <li><a href="{rel}business/cubicle/">キュービクルの更新</a></li>
          <li><a href="{rel}shanetsu-chiba/">千葉の遮熱（専門ページ）</a></li>
        </ul>'''
        col2 = f'''<h4>会社情報・相談</h4><ul>
          <li><a href="{rel}company.html">会社案内</a></li>
          <li><a href="{rel}terasaki_lp.html">代表者プロフィール</a></li>
          <li><a href="{rel}faq.html">よくあるご質問</a></li>
          <li><a href="{FORMS}" target="_blank" rel="noopener">無料診断・お問い合わせ</a></li>
          <li><a href="{rel}residential/">ご家庭の方はこちら</a></li>
          <li><a href="{rel}privacy.html">プライバシーポリシー</a></li>
        </ul>'''
        desc = "千葉の企業のための<br>省エネ・創エネ ワンストップ"
    else:
        col1 = f'''<h4>住まいの困りごと</h4><ul>
          <li><a href="{rel}residential/#komarigoto">困りごとから探す（住宅）</a></li>
          <li><a href="{rel}residential/ecocute/">エコキュートの交換・故障</a></li>
          <li><a href="{rel}residential/solar/">太陽光は元が取れるか</a></li>
          <li><a href="{rel}residential/battery/">蓄電池は必要か・停電で何時間</a></li>
          <li><a href="{rel}sotsu-fit/">卒FIT後どうするか</a></li>
        </ul>'''
        col2 = f'''<h4>会社情報・相談</h4><ul>
          <li><a href="{rel}company.html">会社案内</a></li>
          <li><a href="{rel}service.html">給湯器・エコキュートのサービス</a></li>
          <li><a href="{rel}faq.html">よくあるご質問</a></li>
          <li><a href="{rel}contact.html">お問い合わせ</a></li>
          <li><a href="{rel}">法人の方はこちら</a></li>
          <li><a href="{rel}privacy.html">プライバシーポリシー</a></li>
        </ul>'''
        desc = "千葉のご家庭の<br>暑さ寒さ・電気代・設備・停電の相談窓口"
    # 画面下の固定バー（スマホのみ表示）：相談する ｜ LINEで送る
    if p["audience"] == "business":
        sticky = f'''<div class="sticky-cta" aria-label="相談する">
  <a class="s1" href="{FORMS}" target="_blank" rel="noopener" data-event="cta_click" data-cta-type="sticky_consult" data-cta-position="sticky">{MAIL_SVG}相談する</a>
  <a class="s2" href="{LINE_B}" target="_blank" rel="noopener" data-event="line_click" data-cta-position="sticky" data-line-account="@119upwsl">{LINE_SVG}LINEで送る</a>
</div>'''
    else:
        sticky = f'''<div class="sticky-cta" aria-label="相談する">
  <a class="s1" href="{rel}contact.html" data-event="cta_click" data-cta-type="sticky_consult" data-cta-position="sticky">{MAIL_SVG}相談する</a>
  <a class="s2" href="{LINE_R}" target="_blank" rel="noopener" data-event="line_click" data-cta-position="sticky" data-line-account="@631cqlgf">{LINE_SVG}LINEで送る</a>
</div>'''
    return f'''<footer class="footer">
  <div class="wrap">
    <div class="footer-grid">
      <div><div class="name">シスコムサステナシールド</div><div class="desc">{desc}<br>代表 寺嵜忠弘<br>株式会社シスコムネット代理店</div></div>
      <div>{col1}</div>
      <div>{col2}</div>
    </div>
    <div class="footer-bottom"><span>© 2026 シスコムサステナシールド ／ 寺嵜忠弘</span><span><a href="{rel}privacy.html">プライバシーポリシー</a></span></div>
  </div>
</footer>
{sticky}
{DRAWER_JS}
</body>
</html>
'''

def trust_block(audience):
    if audience == "business":
        items = [
            ("まず測る", "サーモカメラで屋根・天井・窓の温度分布を、電力データで負荷の時間帯を確認します。感覚や一般論ではなく、御社の建物の数字で判断します。"),
            ("不要なら不要と言う", "測った結果、設備交換や工事が最善でない場合は、そのままお伝えします。運用の見直しや部分対応で済むなら、その提案で終わります。"),
            ("交換を前提にしない", "既設の設備・屋根・契約を活かせる可能性から順に検討します。費用の大きい選択肢は、比較材料をそろえてからご判断いただきます。"),
        ]
    else:
        items = [
            ("まず測る", "写真・検針票・使用状況から、どこにお金と熱が逃げているかを確認します。感覚や一般論ではなく、お宅の条件で判断します。"),
            ("不要なら不要と言う", "確認した結果、今の設備を使い続けるのが最善なら、そうお伝えします。修理で済むなら交換は勧めません。"),
            ("交換を前提にしない", "今ある設備・屋根・契約を活かせる可能性から順に検討します。費用の大きい選択肢は、比較材料をそろえてからご判断いただけます。"),
        ]
    lis = "".join(f'<div class="trust-item"><h3>{esc(h)}</h3><p>{esc(t)}</p></div>' for h, t in items)
    return f'''<section class="section trust" id="trust">
  <div class="wrap">
    <h2 class="h2">まず測る 不要なら不要と言う</h2>
    <p class="lead">サーモカメラ・電力データ・現地条件を確認してから提案します。設備交換を前提にしません。</p>
    <div class="trust-grid">{lis}</div>
  </div>
</section>
'''

def cta_block(p):
    photo = f'{p["rel"]}assets/terasaki-profile.jpg'
    if p["audience"] == "business":
        primary = f'<a class="btn btn-gold" href="{FORMS}" target="_blank" rel="noopener" data-event="cta_click" data-cta-type="{p["cta_type"]}" data-cta-position="final">{esc(p["cta_label"])}</a>'
        line = f'<a class="btn btn-line" href="{LINE_B}" target="_blank" rel="noopener" data-event="line_click" data-cta-position="final" data-line-account="@119upwsl">{LINE_SVG}写真・図面をLINEで送って見てもらう</a>'
    else:
        primary = f'<a class="btn btn-gold" href="{p["rel"]}contact.html" data-event="cta_click" data-cta-type="{p["cta_type"]}" data-cta-position="final">{esc(p["cta_label"])}</a>'
        line = f'<a class="btn btn-line" href="{LINE_R}" target="_blank" rel="noopener" data-event="line_click" data-cta-position="final" data-line-account="@631cqlgf">{LINE_SVG}写真をLINEで送って見てもらう</a>'
    return f'''<div class="cta-box" id="soudan">
      <div class="face"><img src="{photo}" alt="代表 寺嵜忠弘"></div>
      <div>
        <div class="who">代表 寺嵜忠弘 ｜ 電気業界27年 ｜ 千葉拠点</div>
        <h3>{p["cta_head"]}</h3>
        <p>{esc(p["cta_sub"])}</p>
        <div class="btns">{primary}{line}</div>
        <p class="tel">お電話でも承ります <a href="{TEL}">{TEL_DISP}</a></p>
        <p class="small">{esc(p["cta_note"])}</p>
      </div>
    </div>'''

def kadai_page(p):
    out = head(p) + header(p)
    # HERO
    chips = "".join(f'<a href="#{a}">{esc(t)}</a>' for t, a in p["chips"])
    out += f'''<section class="hero">
  <div class="hero-inner">
    <div>
      <div class="eyebrow">{esc(p["eyebrow"])}</div>
      <h1>{p["h1"]}</h1>
      <p class="lead">{p["lead"]}</p>
      <div class="hero-cta">
        <a class="btn btn-gold" href="#soudan">{esc(p["cta_label"])}</a>
        <a class="btn btn-ghost" href="#paths">解決策の分かれ道を見る</a>
      </div>
      <div class="hero-meta">{p["hero_meta"]}</div>
    </div>
    <div>
      {hero_figure(p["file"], p["rel"], p["photo_alt"], p["photo_caption"])}
    </div>
  </div>
</section>

<section class="section first" id="anata">
  <div class="wrap">
    <h2 class="h2">あなたの場合は どれに近いですか</h2>
    <p class="lead">近いものを選ぶと、その項目へ移動します。選ばなくても、下へ進めば解決策と相談先まで読めます。</p>
    <div class="chips">{chips}</div>
  </div>
</section>
'''
    # SCENE
    out += f'''<section class="section alt" id="scene">
  <div class="wrap">
    <h2 class="h2">{p["scene_h2"]}</h2>
    <div class="scene">
      <div class="tag">例えばこんな場面</div>
      {p["scene_body"]}
      <div class="view">{p["scene_view"]}</div>
    </div>
  </div>
</section>
'''
    # CAUSES
    causes = "".join(f'<div class="cause" id="{a}"><h3>{esc(h)}</h3><p>{esc(t)}</p></div>' for a, h, t in p["causes"])
    out += f'''<section class="section" id="genin">
  <div class="wrap">
    <h2 class="h2">{p["causes_h2"]}</h2>
    <p class="lead">{esc(p["causes_lead"])}</p>
    <div class="cause-grid">{causes}</div>
  </div>
</section>
'''
    # CHECK
    checks = "".join(f'<li>{esc(c)}</li>' for c in p["checks"])
    out += f'''<section class="section alt" id="kakunin">
  <div class="wrap">
    <h2 class="h2">まず確認するもの</h2>
    <p class="lead">{esc(p["checks_lead"])}</p>
    <div class="check"><ul>{checks}</ul><p class="hint">{esc(p["checks_hint"])}</p></div>
  </div>
</section>
'''
    # PATHS
    paths = ""
    for role, h, t, fit, href, label, main in p["paths"]:
        cls = "path main" if main else "path"
        link = f'<a class="more" href="{href}">{esc(label)}</a>' if href else ""
        paths += f'<div class="{cls}"><div class="role">{esc(role)}</div><h3>{esc(h)}</h3><p>{esc(t)}</p><div class="fit">{fit}</div>{link}</div>'
    out += f'''<section class="section" id="paths">
  <div class="wrap">
    <h2 class="h2">{p["paths_h2"]}</h2>
    <p class="lead">{esc(p["paths_lead"])}</p>
    <div class="paths">{paths}</div>
    <div class="nogo"><h3>やらない判断</h3><p>{esc(p["nogo"])}</p></div>
  </div>
</section>
'''
    # COST
    costs = "".join(f'<li><b>{esc(b)}</b> {esc(t)}</li>' for b, t in p["costs"])
    out += f'''<section class="section alt" id="hiyou">
  <div class="wrap">
    <h2 class="h2">費用の決まり方</h2>
    <p class="lead">{esc(p["costs_lead"])}</p>
    <ul class="cost-list">{costs}</ul>
    <p class="note">{esc(p["costs_note"])}</p>
  </div>
</section>
'''
    if p.get("extra"):
        out += p["extra"]
    out += trust_block(p["audience"])
    # FAQ
    faqs = "".join(f'<div class="faq-item"><h3>{esc(q)}</h3><p>{esc(a)}</p></div>' for q, a in p["faq"])
    out += f'''<section class="section" id="faq">
  <div class="wrap">
    <h2 class="h2">よくあるご質問</h2>
    {faqs}
  </div>
</section>
'''
    # NEXT
    steps = "".join(f'<div class="step3"><div class="n">0{i+1}</div><h3>{esc(h)}</h3><p>{esc(t)}</p></div>' for i, (h, t) in enumerate(p["next"]))
    out += f'''<section class="section alt" id="next">
  <div class="wrap">
    <h2 class="h2">次の一歩</h2>
    <p class="lead">自分で確認する、家族や社内で話す、寺嵜と整理する。どこから始めても構いません。</p>
    <div class="steps3">{steps}</div>
    {cta_block(p)}
  </div>
</section>
'''
    # RELATED
    def col(h, items):
        lis = "".join(f'<li><a href="{u}">{esc(t)}</a></li>' for t, u in items)
        return f'<div class="related-col"><h4>{esc(h)}</h4><ul>{lis}</ul></div>'
    out += f'''<section class="section related" id="related">
  <div class="wrap">
    <h2 class="h2">次に知りたいこと</h2>
    <div class="related-grid">
      {col("根拠・事例", p["rel_evidence"])}
      {col("関連する困りごと", p["rel_kadai"])}
      {col("入口へ戻る", p["rel_back"])}
    </div>
  </div>
</section>
'''
    out += footer(p)
    return add_en_labels(out)

# ============================================================
# ページ定義
# ============================================================
PAGES = []

# ---------- P0-3 法人 1: 工場・倉庫が暑い ----------
PAGES.append(dict(
    file="business/atsui/index.html", photo_alt="工場・倉庫の屋根と作業場の実写", photo_caption="写真1 現地では屋根裏・天井・窓の温度分布をサーモカメラで測り、測定日・外気温・屋根材を記録します", path="/business/atsui/", rel="../../", audience="business",
    title="工場・倉庫が暑い／空調が効かない 原因を測ってから対策を選ぶ｜千葉｜シスコムサステナシールド",
    og_title="工場・倉庫が暑い／空調が効かない 原因を測ってから対策を選ぶ",
    desc="千葉の工場・倉庫・店舗の暑さは、屋根・窓・換気・空調・機器発熱のどれが原因かで対策が変わります。サーモカメラと現地条件で確認し、遮熱・窓・空調・換気から必要なものだけをご提案。屋根が原因でなければ遮熱は勧めません。",
    crumbs=[("ホーム", "/"), ("困りごとから探す（法人）", "/#komarigoto"), ("工場・倉庫が暑い", "/business/atsui/")],
    eyebrow="法人の困りごと ｜ 工場・倉庫が暑い",
    h1="<span class=\"l\">工場・倉庫が暑い</span><br class=\"pc\"><span class=\"l accent\">原因を測ってから</span> <span class=\"l\">対策を選ぶ</span>",
    lead="屋根の輻射熱か、窓か、換気か、機器の発熱か、空調の能力か。暑さの原因は建物ごとに違います。千葉の工場・倉庫・店舗の暑さを、サーモカメラと現地条件で確認し、必要な対策だけをご提案します。相談は代表の寺嵜が直接対応します。",
    hero_meta="対応エリア：<b>市原・千葉・市川・船橋・木更津・君津・富津・袖ケ浦</b> ほか千葉県内",
    cta_label="サーモ計測と現地確認を申し込む", cta_type="hvac_precheck",
    cta_head="暑さの原因を 測ってから決めませんか",
    cta_sub="屋根・天井・窓・空調・換気の温度分布と現地条件を確認し、必要な対策と不要な対策を分けてお伝えします。",
    cta_note="相談・現地確認は無料です。工事を前提にした営業はしません。",
    chips=[("屋根の下が特に暑い", "c-roof"), ("窓際・西日が暑い", "c-window"), ("空調はあるのに効かない", "c-ac"), ("熱がこもって抜けない", "c-vent"), ("機械の周りが暑い", "c-heat")],
    scene_h2="「空調を増やすか 屋根を塗るか」で意見が割れる前に",
    scene_body="<p>午後2時、2階倉庫の温度計は事務所より10度近く高い。事務所の冷房は効いているのに、現場の人だけが暑さをがまんしている。工場長は「空調を増設したい」、経理は「電気代がさらに上がる」、社長は「屋根を塗れば解決すると聞いた」と、三者の話がかみ合わない。</p>",
    scene_view="見方を変える：増設か遮熱かを先に決めるのではなく、屋根裏・天井・窓・作業位置の温度差を測ると、熱がどこから入っているかが分かります。対策の順番は、その後に決めれば十分です。",
    causes_h2="考えられる原因は 大きく5つ",
    causes_lead="複数が重なっていることも多く、どれが支配的かで打ち手が変わります。",
    causes=[
        ("c-roof", "屋根の輻射熱", "金属屋根・折板屋根は日射で表面温度が上がり、天井のない建物では熱がそのまま室内へ放射されます。屋根下だけが暑い場合の主因です。"),
        ("c-window", "窓・ガラス面", "西日や南面の大きなガラスから熱が入ります。窓際の席や陳列棚だけ暑い場合は、屋根より窓の対策が先です。"),
        ("c-vent", "換気不足", "熱気が上部にたまり抜けないと、空調をかけても室温が下がりません。換気扇の位置・風量・給気口の有無で変わります。"),
        ("c-ac", "空調の能力・配置・運転", "能力不足、吹出位置、フィルター詰まり、設定温度や運転時間の問題で効かないことがあります。増設の前に運転状況の確認が必要です。"),
        ("c-heat", "機器の発熱", "生産設備・コンプレッサー・照明の発熱が室内にこもる場合、屋根や窓を対策しても局所の暑さは残ります。"),
    ],
    checks_lead="以下がそろうと、原因の切り分けと概算の精度が上がります。そろっていなくても相談できます。",
    checks=["サーモカメラによる屋根裏・天井・窓・壁・作業位置の温度分布（午後の時間帯）", "屋根材の種類と断熱材の有無、天井の有無と高さ", "窓の向き・面積・ガラスの種類、西日の当たる時間", "空調の型式・台数・設定温度・運転時間・フィルター清掃の状況", "換気扇の位置と風量、給気口の有無", "発熱する設備の位置と稼働時間"],
    checks_hint="現地では当社がサーモカメラで測定します。事前に温度計で「屋根下」と「事務所」の午後の温度差をメモしておくだけでも判断材料になります。",
    paths_h2="解決策の分かれ道",
    paths_lead="原因に合わせて、主な解決策・代わりの選択肢・やらない判断を並べます。",
    paths=[
        ("主な解決策", "屋根の遮熱（遮熱断熱コーティング）", "屋根の輻射熱が支配要因の場合。屋根表面と天井裏の温度上昇を抑え、空調の負荷を下げます。屋根の塗り替え時期と重なる場合は同時に検討します。", "<b>向く：</b>屋根下が突出して暑い、天井がない、金属・折板屋根<br><b>向かない：</b>屋根裏と室内の温度差が小さい", "../../shanetsu-chiba/", "千葉の遮熱（専門ページ）を見る", True),
        ("代わりの選択肢", "窓のコーティング・遮熱", "窓際だけが暑い、西日が強い場合。屋根に手を付けずに、ガラス面からの熱を抑えます。", "<b>向く：</b>ガラス面が大きい店舗・事務所・西向きの作業場<br><b>向かない：</b>窓が小さい倉庫", "../../lp/#window", "窓ガラスコーティングの説明を見る", False),
        ("代わりの選択肢", "換気・空調運転の見直し", "熱気が抜けない、空調の運転に無理がある場合。換気経路の改善や運転の見直しで、工事を最小限にします。", "<b>向く：</b>上部に熱気がたまる、空調の効きにムラがある<br><b>向かない：</b>屋根や窓からの流入が主因", "#soudan", "現地確認で運転と換気を見てもらう", False),
    ],
    nogo="屋根温度が支配要因でない場合、遮熱を単独では勧めません。サーモで屋根裏と室内の温度差が小さいときは、原因が換気・空調運転・機器発熱にあることが多く、屋根を塗っても体感は変わりにくいためです。その場合は、換気や運転の見直しを先にご提案し、遮熱は見送ります。",
    costs_lead="金額は建物ごとに異なるため、一律の価格は掲載していません。決まる要素を先にお伝えします。",
    costs=[("面積と屋根形状", "塗布面積、勾配、折板か平板か、突起物の多さ"), ("下地の状態", "錆・劣化・雨漏りの有無と補修の要否"), ("足場・安全対策", "高さ、周囲の状況、稼働中の作業との調整"), ("仕様と塗布量", "遮熱・断熱・防水のどこまでを求めるか"), ("工期と時期", "夏前の繁忙期か、操業を止めずに施工できるか"), ("補助金", "年度・公募・要件で対象と補助率が変わります")],
    costs_note="遮熱と空調増設で迷う場合は、工事費だけでなく、電気代の変化と耐用年数を並べて比較します。数値は現地条件で変動し、効果を保証するものではありません。",
    faq=[
        ("遮熱だけで室温はどれくらい下がりますか", "屋根材・天井の有無・換気・空調の条件で変わるため、一律の数値は断定しません。現地でサーモ計測をしてから、御社の建物での見込みをお伝えします。屋根が主因でない場合は、遮熱では体感が変わりにくいこともそのままお伝えします。"),
        ("空調を増設した方が早いですか", "場合によります。屋根や窓から入る熱が大きいまま増設すると、電気代が増えても体感が改善しないことがあります。増設費と電気代の変化、遮熱や換気との組み合わせを並べて比較したうえで判断してください。"),
        ("夏前に間に合いますか", "工期は面積・下地・天候・足場の条件で変わります。時期が決まっている場合は、先に現地確認をして工程を組みます。間に合わない場合は、その旨と代替の暑さ対策をお伝えします。"),
        ("補助金は使えますか", "省エネ改修の補助制度は年度・公募時期・要件で変わります。対象になり得るかは、設備と工事内容を確認したうえで、最新の公募要領をもとにご案内します。対象と断定することはありません。"),
    ],
    next=[("自分で確認する", "午後2時から4時の間に、屋根下と事務所の温度差、窓際と室内中央の温度差を温度計で記録してみてください。差が大きい場所が対策の起点です。"), ("社内で話す", "増設・遮熱・換気・窓の4つを候補として並べ、現場・経理・経営でそれぞれの優先順位を出しておくと、提案の比較が早くなります。"), ("寺嵜と整理する", "サーモ計測と現地条件の確認を行い、必要な対策と不要な対策を分けてお伝えします。相談と現地確認は無料です。")],
    rel_evidence=[("自社ビルでの電気代実測（本社施工の記録）", "../../#jisseki"), ("電気代削減シミュレーター（建物用途別の目安）", "../../simulator/")],
    rel_kadai=[("電気代・デマンドが高い", "../denkidai/"), ("屋根の雨漏り・錆・暑さをまとめて直したい", "../../lp/#triple-guard")],
    rel_back=[("困りごとから探す（法人）", "../../#komarigoto"), ("よくあるご質問", "../../faq.html")],
))

# ---------- P0-3 法人 2: 電気代・デマンドが高い ----------
PAGES.append(dict(
    file="business/denkidai/index.html", photo_alt="電気料金明細と30分値グラフの実写", photo_caption="写真1 明細の内訳と最大需要の発生時刻。御社の資料を見ながら整理します", path="/business/denkidai/", rel="../../", audience="business",
    title="電気代・デマンドが高い 明細と30分値で原因から分ける｜千葉の工場・倉庫・店舗｜シスコムサステナシールド",
    og_title="電気代・デマンドが高い 明細と30分値で原因から分ける",
    desc="工場・倉庫・店舗の電気代が高い原因は、基本料金のピーク（デマンド）・空調・稼働時間・契約・負荷の偏りに分かれます。電気料金明細と30分値で原因を切り分け、運用改善・遮熱・EMS・自家消費太陽光・設備更新から必要なものだけを提案します。",
    crumbs=[("ホーム", "/"), ("困りごとから探す（法人）", "/#komarigoto"), ("電気代・デマンドが高い", "/business/denkidai/")],
    eyebrow="法人の困りごと ｜ 電気代・デマンドが高い",
    h1="<span class=\"l\">電気代・デマンドが高い</span><br class=\"pc\"><span class=\"l accent\">明細と30分値で</span> <span class=\"l\">原因から分ける</span>",
    lead="電気代が上がった理由は、単価の値上がりだけとは限りません。基本料金を決めるピーク、空調の負荷、稼働の時間帯、契約種別、設備の同時起動。どれが効いているかで打ち手が変わります。電気料金明細と30分値をもとに、工事が要らない改善から順に整理します。",
    hero_meta="対応：<b>高圧・低圧の工場・倉庫・店舗・事務所</b>（千葉県内を中心に）",
    cta_label="電気料金明細と30分値で確認する", cta_type="demand_check",
    cta_head="電気料金明細と30分値を 一緒に読みませんか",
    cta_sub="直近12か月の明細と30分値があれば、ピークの発生時刻と原因の候補まで整理できます。手元にない場合の取り寄せ方もご案内します。",
    cta_note="相談は無料です。契約や設備の変更を前提にした営業はしません。",
    chips=[("基本料金が下がらない", "c-peak"), ("夏と冬だけ跳ね上がる", "c-ac"), ("使い方は変えていないのに上がった", "c-contract"), ("設備を増やしてから高い", "c-load"), ("太陽光で下げられるか知りたい", "c-solar")],
    scene_h2="「使い方は変えていない」のに 上がり続ける理由",
    scene_body="<p>経理から「去年より電気代が上がっている」と言われ、現場は「使い方は変えていない」と答える。実は、夏の午後の30分間に空調と設備が同時に立ち上がった値が、その後1年間の基本料金を決めていた。誰も間違っていないのに、誰も原因を見ていなかった。</p>",
    scene_view="見方を変える：高圧契約では、基本料金の元になる契約電力が過去1年間の最大需要電力（デマンド）で決まる方式が一般的です。単価ではなく「いつ、何が同時に動いたか」を見ると、工事なしで下げられる部分が見えてきます。",
    causes_h2="電気代が高い原因は 5つに分かれます",
    causes_lead="どれが効いているかは、明細の内訳と30分値を見れば切り分けられます。",
    causes=[
        ("c-peak", "基本料金のピーク（デマンド）", "短時間の最大需要が基本料金を押し上げます。同時起動や夏の午後の重なりが原因なら、運用で下げられる余地があります。"),
        ("c-ac", "空調の負荷", "夏冬に電力量が跳ね上がる場合は、空調が主因です。建物の熱の入り方（屋根・窓）と運転方法の両方を見ます。"),
        ("c-contract", "契約種別・契約電力", "使用実態と契約プランが合っていないと、使い方を変えなくても割高になります。プランの見直しだけで済むこともあります。"),
        ("c-load", "負荷の偏り・同時起動", "設備を増やした後に高くなった場合、起動時刻の重なりや力率の低下が影響していることがあります。"),
        ("c-solar", "自家消費の余地", "昼間の使用が多い事業所では、自家消費太陽光で購入電力を減らせる可能性があります。ただし採算は屋根条件と使用パターン次第です。"),
    ],
    checks_lead="次の資料があると、原因の切り分けと対策の優先順位がつけられます。",
    checks=["電気料金明細（直近12か月分。基本料金・電力量料金・燃料費調整・再エネ賦課金の内訳）", "30分値（スマートメーターのデータ。電力会社の会員ページから取得できる場合があります）", "最大需要電力の発生した月・日・時刻", "主な設備の稼働スケジュールと起動時刻", "空調の型式・台数・設定・運転時間", "屋根の種類と面積、昼間の稼働時間（自家消費太陽光を検討する場合）"],
    checks_hint="30分値の取り方が分からない場合は、契約中の電力会社と契約種別を教えていただければ手順をご案内します。",
    paths_h2="解決策の分かれ道",
    paths_lead="工事の要らない改善から順に並べます。組み合わせることもあります。",
    paths=[
        ("主な解決策", "省エネ（遮熱・窓）と自家消費太陽光の組み合わせ", "空調負荷が主因で、昼間の使用が多い事業所向け。建物に入る熱を減らしてから、昼間の電力を自家消費でまかなう順番で考えます。", "<b>向く：</b>夏冬の電力量が大きい、屋根面積がある、昼間稼働<br><b>向かない：</b>夜間中心の稼働、屋根が使えない", "../../lp/", "省エネ・創エネ ダブルプランを見る", True),
        ("代わりの選択肢", "運用改善・デマンド監視（EMS）", "同時起動やピークの重なりが主因の場合。起動時刻の分散、設定温度の見直し、デマンド監視で工事なしに基本料金を抑えます。", "<b>向く：</b>ピークが短時間に集中している<br><b>向かない：</b>常時高負荷で平準化の余地がない", "#soudan", "30分値を見て運用改善の余地を確認する", False),
        ("代わりの選択肢", "屋根の遮熱で空調負荷を下げる", "屋根の輻射熱で空調が働きすぎている場合。屋根の塗り替え時期と合わせると効率的です。", "<b>向く：</b>屋根下が暑い、金属・折板屋根<br><b>向かない：</b>屋根が主因でない", "../../shanetsu-chiba/", "千葉の遮熱（専門ページ）を見る", False),
    ],
    nogo="ピークが空調由来でない場合、遮熱や窓の工事は勧めません。契約種別の見直しや起動時刻の分散だけで下がる場合は、設備投資を提案せずそこで終わります。自家消費太陽光も、昼間の使用が少ない事業所には採算が合わないことをそのままお伝えします。",
    costs_lead="対策ごとに費用の決まり方が違います。共通するのは、明細と30分値がないと概算も出せないことです。",
    costs=[("運用改善", "費用は原則かかりません。設備の起動時刻・設定の変更で対応します"), ("デマンド監視・EMS", "監視点数、既存設備との接続、通知や制御の範囲"), ("遮熱・窓", "面積・下地・足場・仕様（工場・倉庫が暑いページを参照）"), ("自家消費太陽光", "屋根条件・容量・架台・電気工事・購入かリースかPPAか"), ("設備更新", "型式・容量・工事範囲・停電作業の有無"), ("補助金", "年度・公募・要件で対象と補助率が変わります")],
    costs_note="削減額の見込みは、御社の30分値と電力単価をもとに条件付きでお伝えします。固定の削減率を約束することはありません。",
    faq=[
        ("電気代はどれくらい下がりますか", "原因と対策の組み合わせで変わるため、明細と30分値を見る前に数値は断定しません。確認後に、条件を明記した見込みをお伝えします。"),
        ("30分値はどこで手に入りますか", "多くの電力会社では、契約者向けの会員ページやスマートメーターの計量データから取得できます。契約先と契約種別を教えていただければ、取得手順をご案内します。"),
        ("契約プランの見直しだけでも相談できますか", "できます。見直しだけで済む場合は、設備や工事の提案はしません。"),
        ("太陽光を載せれば電気代はゼロになりますか", "なりません。夜間や曇天時は購入電力が残り、基本料金も残ります。昼間の使用量・屋根条件・買取条件をもとに、条件付きで採算を試算します。"),
    ],
    next=[("自分で確認する", "直近12か月の明細で、基本料金と電力量料金のどちらが増えたかを見てください。基本料金が増えていればピーク、電力量が増えていれば使い方か単価が原因の候補です。"), ("社内で話す", "設備の起動時刻を一覧にして、同じ30分に重なっているものがないか確認しておくと、運用改善の余地が見えます。"), ("寺嵜と整理する", "明細と30分値をもとに、工事の要らない改善から順に整理してお伝えします。相談は無料です。")],
    rel_evidence=[("自社ビルでの電気代実測（本社施工の記録）", "../../#jisseki"), ("電気代削減シミュレーター（建物用途別の目安）", "../../simulator/")],
    rel_kadai=[("工場・倉庫が暑い／空調が効かない", "../atsui/"), ("キュービクルの更新時期が不安", "../cubicle/")],
    rel_back=[("困りごとから探す（法人）", "../../#komarigoto"), ("よくあるご質問", "../../faq.html")],
))

# ---------- P0-3 法人 3: キュービクル更新 ----------
PAGES.append(dict(
    file="business/cubicle/index.html", photo_alt="キュービクルの銘板と盤内の実写", photo_caption="写真1 銘板・設置年・点検報告。更新範囲はここから決めます", path="/business/cubicle/", rel="../../", audience="business",
    title="キュービクル・受変電設備の更新時期が不安 銘板と点検報告で更新範囲を決める｜千葉｜シスコムサステナシールド",
    og_title="キュービクルの更新時期が不安 銘板と点検報告で更新範囲を決める",
    desc="キュービクル（高圧受変電設備）の更新目安、費用の決まり方、停電時間、部分更新の可否を整理。銘板・設置年・単線結線図・点検報告書をもとに、部分更新・全更新・機器単位更新・工程分割から更新範囲を決めます。電気工事27年の代表が対応。",
    crumbs=[("ホーム", "/"), ("困りごとから探す（法人）", "/#komarigoto"), ("キュービクルの更新", "/business/cubicle/")],
    eyebrow="法人の困りごと ｜ キュービクルの更新",
    h1="<span class=\"l\">キュービクル更新が不安</span><br class=\"pc\"><span class=\"l accent\">銘板と点検報告で</span> <span class=\"l\">更新範囲を決める</span>",
    lead="「そろそろ更新を」と言われたが、いくらかかるのか、何日止まるのか、全部替える必要があるのかが分からない。キュービクルの更新は、銘板・設置年・点検報告書を見れば、範囲と工程の見通しが立ちます。電気工事27年の代表が、更新の要否から工程の分け方までご一緒に整理します。",
    hero_meta="対応：<b>工場・倉庫・店舗・ビル・施設の高圧受変電設備</b>（千葉県内を中心に）",
    cta_label="銘板・点検報告で更新範囲を確認する", cta_type="cubicle_precheck",
    cta_head="銘板の写真と点検報告書で 更新範囲の見通しを",
    cta_sub="全交換が必要とは限りません。劣化した機器だけの部分更新や、停電を短く分ける工程分割も含めて、選択肢を並べてお伝えします。",
    cta_note="相談は無料です。更新を前提にした営業はしません。",
    chips=[("点検で指摘を受けた", "c-inspect"), ("設置から年数が経っている", "c-age"), ("停電を何時間できるか分からない", "c-outage"), ("費用の目安が分からない", "c-cost"), ("一部だけ替えられるか知りたい", "c-partial")],
    scene_h2="「全部替えないと危ない」と言われたときに",
    scene_body="<p>年次点検のあと、「そろそろ全交換を」と見積が届いた。設置から20年以上と聞けば不安になるが、点検報告書の指摘は変圧器1台とコンデンサだけ。全交換の金額と、丸1日の停電を見て、社長は返事を保留したまま半年が過ぎた。</p>",
    scene_view="見方を変える：更新推奨時期は目安であり、機器ごとに状態は違います。点検報告書の指摘機器、製造年、負荷の状況を並べると、今すぐ替えるもの・数年後でよいもの・当面そのままでよいものに分かれます。停電時間も、工程を分ければ短くできることがあります。",
    causes_h2="更新前に知りたい 4つのこと",
    causes_lead="不安の正体は、たいてい次の4つが分からないことです。",
    causes=[
        ("c-age", "更新の目安", "設置年・製造年、メーカーの更新推奨時期、点検での指摘、使用環境（塩害・粉じん・温度）で判断します。年数だけで一括更新とは決めません。"),
        ("c-cost", "費用の決まり方", "容量、機器構成（変圧器・遮断器・コンデンサ・保護継電器など）、工事範囲、停電作業の有無、搬入条件、廃棄で決まります。"),
        ("c-outage", "停電時間", "全更新なら長時間の停電が必要なことがあります。機器単位の更新や工程の分割、仮設電源の利用で短縮できる場合があります。"),
        ("c-partial", "部分更新の可否", "劣化した機器だけを更新できるか、盤の構造・スペース・他機器との組合せで決まります。銘板と結線図があれば見通しが立ちます。"),
        ("c-inspect", "点検指摘の読み方", "指摘は「今すぐ」「計画的に」「経過観察」に分かれます。どの区分かで、更新の順番と時期が変わります。"),
    ],
    checks_lead="次の資料がそろうと、更新範囲と工程の見通しが立ちます。写真だけでも構いません。",
    checks=["銘板の写真（メーカー・型式・製造年・容量）。変圧器・遮断器・コンデンサなど機器ごと", "設置年と、これまでの更新・修理の履歴", "単線結線図（なければ盤内の全景写真）", "直近の点検報告書（指摘事項と区分）", "契約電力と、負荷の増減予定", "停電できる曜日・時間帯と、止められない設備"],
    checks_hint="資料が見つからない場合は、盤の外観と銘板の写真から確認を始めます。危険な位置での撮影はしないでください。扉を開ける必要がある場合は当社が対応します。",
    paths_h2="更新範囲の分かれ道",
    paths_lead="点検指摘・製造年・停電条件から、更新の範囲と順番を決めます。",
    paths=[
        ("主な解決策", "点検報告と銘板から更新範囲を決める", "指摘機器と製造年をもとに、部分更新・全更新・機器単位更新・工程分割のどれが合うかを整理し、停電時間と費用の見通しを並べます。", "<b>向く：</b>更新の要否や範囲が分からない、複数の見積で迷っている<br><b>向かない：</b>すでに範囲と工程が確定している", "#soudan", "銘板・点検報告で更新範囲を確認する", True),
        ("代わりの選択肢", "更新と同時に契約・負荷を見直す", "更新のタイミングで、契約電力・力率・デマンドの状況も確認すると、容量の選定と電気代の両方に効きます。", "<b>向く：</b>負荷の増減予定がある、基本料金が高い<br><b>向かない：</b>負荷が安定している", "../denkidai/", "電気代・デマンドが高い", False),
        ("代わりの選択肢", "自家消費太陽光と同時に検討する", "屋根面積があり昼間稼働の事業所では、受変電設備の更新と合わせて自家消費太陽光の接続を検討すると、工事の重複を避けられます。", "<b>向く：</b>屋根が使える、昼間の使用が多い<br><b>向かない：</b>夜間中心、屋根が使えない", "../../lp/#order", "太陽光と蓄電池の説明を見る", False),
    ],
    nogo="点検で指摘がなく、製造年が浅い機器まで一括で更新することは勧めません。更新推奨時期は目安であり、使用環境と点検結果で判断します。また、消防や電気設備の法令適合、停電の可否、価格は、現地と資料を確認するまで断定しません。",
    costs_lead="費用は機器構成と工事条件で大きく変わるため、一律の金額は掲載していません。",
    costs=[("容量と機器構成", "変圧器の容量・台数、遮断器・コンデンサ・保護継電器の有無"), ("更新範囲", "部分更新か全更新か、盤ごとの交換か機器単位か"), ("停電作業", "停電の可否・時間帯、仮設電源の要否"), ("搬入・設置条件", "クレーンの可否、通路、屋上か地上か、基礎の状態"), ("廃棄・処分", "旧機器の撤去と処分（PCB含有の有無確認を含む）"), ("補助金", "省エネ性能の高い変圧器などは対象になる制度が存在する年度があります。要件は都度確認します")],
    costs_note="複数の見積がある場合は、範囲と工程の前提が同じかを確認してから比較します。金額だけの比較はおすすめしません。",
    faq=[
        ("設置から何年で更新が必要ですか", "機器ごとにメーカーの更新推奨時期の目安がありますが、使用環境と点検結果で実際の状態は異なります。年数だけで判断せず、銘板と点検報告書をもとに機器ごとに整理します。"),
        ("停電なしで更新できますか", "受変電設備の更新では停電を伴う作業が基本です。工程分割や仮設電源で停電時間を短くできる場合がありますが、停電なしと断定することはありません。現地条件を確認したうえでお伝えします。"),
        ("一部の機器だけ替えられますか", "盤の構造・スペース・他機器との組合せによります。銘板と結線図から可否の見通しを立て、部分更新が合理的な場合はその案をお出しします。"),
        ("点検業者の見積が高い気がします", "範囲と工程の前提を確認してから比較します。同じ前提で並べたうえで、不要な範囲が含まれていればそのままお伝えします。"),
    ],
    next=[("自分で確認する", "直近の点検報告書の指摘欄を見て、「今すぐ」「計画的に」「経過観察」のどれに区分されているかを確認してください。銘板の写真も撮っておくと早いです。"), ("社内で話す", "停電できる曜日・時間帯と、絶対に止められない設備を一覧にしておくと、工程の分け方が決めやすくなります。"), ("寺嵜と整理する", "銘板・点検報告・結線図をもとに、更新の範囲と順番、停電時間の見通しを整理してお伝えします。相談は無料です。")],
    rel_evidence=[("代表者プロフィール（電気工事27年の経歴）", "../../terasaki_lp.html"), ("会社案内", "../../company.html")],
    rel_kadai=[("電気代・デマンドが高い", "../denkidai/"), ("停電時に何時間動かせるか知りたい", "../../lp/#order")],
    rel_back=[("困りごとから探す（法人）", "../../#komarigoto"), ("よくあるご質問", "../../faq.html")],
))

# ---------- P0-4 住宅 1: エコキュート交換 ----------
PAGES.append(dict(
    file="residential/ecocute/index.html", photo_alt="エコキュートの設置場所（全景・ヒートポンプ前面・基礎配管）の実写", photo_caption="写真1 設置場所の写真3枚で5点を確認します", path="/residential/ecocute/", rel="../../", audience="residential",
    title="エコキュートの交換費用と故障 直すか替えるかを先に整理｜千葉｜シスコムサステナシールド",
    og_title="エコキュートの交換費用と故障 直すか替えるかを先に整理",
    desc="エコキュートの故障症状・交換時期・費用の決まり方・通常型とおひさまエコキュートの違い・設置場所の確認・補助制度を整理。修理で済む場合は交換を勧めません。設置場所の写真3枚で5点確認。千葉県のご家庭向け。",
    crumbs=[("ホーム", "/"), ("住まいの困りごと", "/residential/"), ("エコキュートの交換・故障", "/residential/ecocute/")],
    eyebrow="住まいの困りごと ｜ エコキュートの交換・故障",
    h1="<span class=\"l\">エコキュートの</span> <span class=\"l\">交換費用と故障</span><br class=\"pc\"><span class=\"l accent\">直すか替えるか</span> <span class=\"l\">先に整理</span>",
    lead="お湯が出ない、エラーが消えない、沸き上げに時間がかかる。そんなとき「もう交換ですね」と言われても、本当にそうか判断できないのが普通です。症状・使用年数・修理費・設置場所を順に確認すれば、修理で済むのか、替えるならどの機種かが見えてきます。修理で済む場合は交換を勧めません。",
    hero_meta="対応：<b>千葉県内のご家庭</b>（型式が分からなくても相談できます）",
    cta_label="設置場所の写真3枚で5点確認", cta_type="ecocute_location_check",
    cta_head="設置場所の写真3枚で 5つの点を確認します",
    cta_sub="写真は最初の確認に使います。機種や設置場所に合わせて、必要な資料と確認事項をご案内します。写真がなくても、故障中でも相談できます。",
    cta_note="必要な写真：設備の全景、ヒートポンプの前面と吹出口、基礎・配管・排水が分かる写真。撮れない場合はそのままご相談ください。",
    chips=[("お湯が出ない・エラーが出る", "c-fault"), ("使用年数が長い", "c-age"), ("交換費用を知りたい", "c-cost"), ("おひさまエコキュートと迷っている", "c-ohisama"), ("設置場所が気になる", "c-place")],
    scene_h2="「10年経ったから交換」で 決めてしまう前に",
    scene_body="<p>朝、シャワーの途中でお湯が水になった。リモコンにはエラー番号。ご主人は「もう10年だし替えよう」、奥さまは「修理で直るなら直したい」。ネットで調べると、交換の広告ばかりが出てくる。どちらが正しいのか、決め手がない。</p>",
    scene_view="見方を変える：エラー番号・使用年数・修理歴・部品の供給状況・修理費と交換費の比較、この5つがそろえば判断できます。年数だけで交換を決める必要はありません。",
    causes_h2="故障の症状と 交換時期の考え方",
    causes_lead="症状によって、修理で済むものと交換を検討するものが分かれます。ここでは断定せず、確認の順番をお伝えします。",
    causes=[
        ("c-fault", "お湯が出ない・エラー表示", "断水や凍結、リモコン設定、ヒートポンプの一時停止など、修理を要しない原因もあります。エラー番号と発生状況を控えて、メーカーの案内と照合します。"),
        ("c-age", "使用年数が長い", "使用年数、修理歴、部品の供給状況、修理費と交換費の比較で判断します。年数だけで交換を決めません。"),
        ("c-cost", "沸き上げに時間がかかる・湯量が足りない", "設定（沸き上げモード・時間帯）、家族構成の変化、ヒートポンプ周りの障害物、配管の断熱など、設定と環境の見直しで改善する場合があります。"),
        ("c-ohisama", "水漏れ・異音", "タンクや配管の接続部、ヒートポンプの振動など、部位で修理可否が変わります。放置すると被害が広がるため、早めに位置を確認します。"),
        ("c-place", "設置場所の不安", "北側にある、浸水が心配、隣家に近い。設置場所の条件は、交換の要否とは別に確認します（下の5点確認を参照）。"),
    ],
    checks_lead="次がそろうと、修理か交換か、交換ならどの機種かの判断が早くなります。",
    checks=["リモコンのエラー番号と、いつ・どんな使い方で出たか", "本体の型式と製造年（タンク側面や取扱説明書に記載）", "使用年数と、これまでの修理歴", "家族構成と入浴の時間帯（湯量と容量の判断に使います）", "太陽光の有無と、昼間の在宅状況（おひさまエコキュートの適否）", "設置場所の写真3枚（全景、ヒートポンプ前面と吹出口、基礎・配管・排水）"],
    checks_hint="型式が分からなくても相談できます。写真が撮れない場合も、状況をお聞きして必要な確認事項をご案内します。",
    paths_h2="解決策の分かれ道",
    paths_lead="修理・継続使用から順に並べます。交換が最善の場合だけ、機種の選び方に進みます。",
    paths=[
        ("主な解決策", "交換（通常型 または おひさまエコキュート）", "修理費が交換費に近い、部品供給が終了している、湯量が家族構成に合っていない場合。太陽光があり昼間に沸き上げできる家はおひさま型、そうでない家は通常型が候補です。", "<b>通常型が向く：</b>太陽光なし、夜間の電気料金が安い契約<br><b>おひさま型が向く：</b>太陽光あり、昼間の余剰電力を使いたい", "../../service.html", "エコキュート交換・新設のサービスを見る", True),
        ("代わりの選択肢", "修理・設定変更・継続使用", "エラーの原因が部品単位で特定でき、部品の供給がある場合。沸き上げ設定や周囲の障害物の改善だけで済むこともあります。", "<b>向く：</b>使用年数が浅い、修理費が明確<br><b>向かない：</b>部品供給が終了、修理を繰り返している", "#soudan", "症状を伝えて修理で済むか確認する", False),
        ("代わりの選択肢", "太陽光・卒FITと合わせて考える", "太陽光がある家や卒FITを迎える家では、昼間の余剰電力でお湯を沸かす使い方が候補になります。給湯器の交換時期と合わせて比較します。", "<b>向く：</b>太陽光あり、卒FIT前後<br><b>向かない：</b>太陽光なし、昼間の余剰がない", "../../sotsu-fit/", "卒FIT後の選択肢を比べる", False),
    ],
    nogo="修理で直り、部品の供給がある場合は交換を勧めません。設置場所も、北側にあることや浸水の心配だけで移設・交換を決めず、現状維持・沸き上げ時間の調整・障害物や排気再循環の改善・浸水対策のかさ上げ・移設または交換の5つを並べて判断します。",
    costs_lead="交換費用は本体だけでは決まりません。決まる要素を先にお伝えします。",
    costs=[("タンク容量と機種", "家族構成と入浴時間帯で容量を選びます。通常型・おひさま型・薄型・高圧型で本体価格が異なります"), ("設置場所と基礎", "既存基礎が使えるか、新設が必要か。搬入経路と設置スペース"), ("配管と電気工事", "配管の再利用可否、200V専用回路の有無と分電盤の状況"), ("既設の撤去・処分", "旧機の撤去と処分費"), ("補助制度", "国の給湯省エネ事業などは年度・機種要件・予算で変わります。最新条件を確認してご案内します"), ("保証", "メーカー保証と工事保証の範囲と年数")],
    costs_note="金額は現地条件と機種で変わるため、一律の価格は掲載していません。見積は内訳（本体・工事・撤去・諸経費）を分けてお出しします。",
    extra='''<section class="section" id="place">
  <div class="wrap">
    <h2 class="h2">置き場所まで選んでこそ エコキュート</h2>
    <p class="lead">南側か北側かだけで決めず、通風、冷たい排気の再吸込み、寝室や窓との距離、配管と排水、浸水リスク、点検空間を確認します。条件によっては交換や移設をせず、運転時間の調整や障害物の改善だけでよい場合もあります。</p>
    <div class="cause-grid">
      <div class="cause"><h3>1 現状維持</h3><p>設置条件に問題がなければ、そのまま使い続けます。</p></div>
      <div class="cause"><h3>2 沸き上げ時間の調整</h3><p>外気温の高い時間帯に沸き上げるなど、設定の見直しで効率と騒音の両方に配慮します。</p></div>
      <div class="cause"><h3>3 障害物・排気再循環の改善</h3><p>ヒートポンプの前の物や壁が近すぎると、冷たい排気を再び吸い込んで効率が落ちます。配置の改善で対応します。</p></div>
      <div class="cause"><h3>4 浸水対策のかさ上げ</h3><p>想定浸水深、基礎と固定、配管、排水、点検空間、貯湯タンクと電気設備まで確認します。かさ上げだけで被害を防げるとは限りません。</p></div>
      <div class="cause"><h3>5 移設または交換</h3><p>上の4つで解決しない場合に検討します。移設先の条件も同じ観点で確認します。</p></div>
    </div>
  </div>
</section>
''',
    faq=[
        ("北側にあると省エネではないですか", "北側にあることだけで不適切とは判断しません。運転時間帯の外気温、通風、排気の再吸込み、騒音、配管、排水、機種別の離隔条件を合わせて確認します。"),
        ("浸水が心配ならかさ上げすれば安心ですか", "想定浸水深、基礎と固定、配管、排水、点検空間、貯湯タンクと電気設備も確認します。かさ上げだけで被害を防げるとは限りません。"),
        ("太陽光がなくてもおひさまエコキュートは意味がありますか", "おひさまエコキュートは昼間に沸き上げる前提の機種です。太陽光がなく昼間の電気料金が高い契約では、通常型の方が合うことが多いです。契約と使い方を見てからお伝えします。"),
        ("故障中ですぐ替えたいのですが", "まずエラー番号と型式を教えてください。修理で復旧できる場合はその案内を、交換が必要な場合は在庫・工期・仮の給湯手段を含めてご案内します。"),
        ("補助金はいくらもらえますか", "国の給湯省エネ事業などの補助制度は、年度・機種要件・予算の状況で変わります。対象機種と申請時期を確認したうえで、最新条件をもとにご案内します。金額を断定することはありません。"),
    ],
    next=[("自分で確認する", "リモコンのエラー番号と、タンク側面の型式・製造年を控えてください。ヒートポンプの前に物が置かれていないかも見ておくと判断が早くなります。"), ("家族で話す", "入浴の時間帯、湯切れの頻度、太陽光の有無を家族で共有しておくと、容量と機種の選び方が決めやすくなります。"), ("寺嵜と整理する", "写真3枚と症状をもとに、修理か交換か、交換ならどの機種かを整理してお伝えします。写真がなくても相談できます。")],
    rel_evidence=[("節約の虎の巻（給湯器の寿命・補助制度の解説）", "../../column.html"), ("よくあるご質問", "../../faq.html")],
    rel_kadai=[("太陽光は元が取れるか", "../solar/"), ("卒FIT後どうするか", "../../sotsu-fit/"), ("停電で何時間使えるか", "../battery/")],
    rel_back=[("住まいの困りごとから探す", "../#komarigoto"), ("給湯器・エコキュートのサービス", "../../service.html")],
))

# ---------- P0-4 住宅 2: 太陽光は元が取れるか ----------
PAGES.append(dict(
    file="residential/solar/index.html", photo_alt="戸建て屋根と検針票の実写", photo_caption="写真1 屋根の向きと面積、検針票12か月分から採算を試算します", path="/residential/solar/", rel="../../", audience="residential",
    title="太陽光は元が取れるか 屋根と電気の使い方で答えが変わる｜千葉のご家庭｜シスコムサステナシールド",
    og_title="太陽光は元が取れるか 屋根と電気の使い方で答えが変わる",
    desc="住宅の太陽光が元を取れるかは、屋根条件・使用電力量・昼間の使用・売電条件・購入かリースかPPAかで変わります。固定の回収年数は断定せず、条件別に試算。向かない家には向かないとお伝えします。千葉県のご家庭向け。",
    crumbs=[("ホーム", "/"), ("住まいの困りごと", "/residential/"), ("太陽光は元が取れるか", "/residential/solar/")],
    eyebrow="住まいの困りごと ｜ 太陽光は元が取れるか",
    h1="<span class=\"l\">太陽光は元が取れるか</span><br class=\"pc\"><span class=\"l accent\">屋根と電気の使い方で</span> <span class=\"l\">答えが変わる</span>",
    lead="「何年で元が取れます」という説明は、前提を変えれば何通りにもなります。屋根の向きと面積、年間の使用電力量、昼間に家で電気を使うかどうか、売電の条件、買い方。この順に確認すると、お宅の場合の答えに近づきます。向かない条件の家には、向かないとお伝えします。",
    hero_meta="対応：<b>千葉県内の戸建て</b>（新築・既築どちらも）",
    cta_label="屋根と検針票で採算の見通しを聞く", cta_type="solar_payback_check",
    cta_head="屋根の写真と検針票12か月分で 条件別の見通しを",
    cta_sub="回収年数は固定の数字ではなく、条件を変えた複数のシナリオでお出しします。導入しない方がよい場合も、その根拠と一緒にお伝えします。",
    cta_note="相談・試算は無料です。訪問販売や即決を求める営業はしません。",
    chips=[("屋根に載るか分からない", "c-roof"), ("昼間は家にいない", "c-daytime"), ("電気代が高くて検討中", "c-usage"), ("売電単価が下がって不安", "c-sell"), ("買うかリースか迷っている", "c-buy")],
    scene_h2="「何年で元が取れる」の 前提を確認する",
    scene_body="<p>訪問してきた営業は「8年で元が取れる」と言い、ネットの記事は「もう元が取れない」と書いている。同じ太陽光なのに正反対。共働きで昼間は誰もいない家と、在宅で昼間に電気を使う家では、同じ設備でも結果が違うことを、どちらも説明していなかった。</p>",
    scene_view="見方を変える：採算を決めるのは設備の性能より、お宅の屋根条件と電気の使い方です。昼間に使う電気が多いほど、売るより使う価値が大きくなります。前提を一つずつ確認すれば、他人の数字に振り回されなくなります。",
    causes_h2="採算を決める 6つの条件",
    causes_lead="上から順に確認します。ひとつでも大きく外れると、結論が変わります。",
    causes=[
        ("c-roof", "屋根条件", "向き・面積・勾配・屋根材・築年数・影の有無。北向き中心や面積が小さい屋根、数年内に葺き替え予定の屋根は、導入を急がない方がよい場合があります。"),
        ("c-usage", "年間の使用電力量", "検針票12か月分で分かります。使用量が多い家ほど、自家消費で減らせる購入電力が大きくなります。"),
        ("c-daytime", "昼間の使用", "在宅の有無、エコキュートの昼間沸き上げ、EVの充電など。昼間に使う電気が多いほど、自家消費率が上がります。"),
        ("c-sell", "売電条件", "買取単価は制度・年度で変わり、以前より下がっています。売電に頼る採算計画は成り立ちにくく、自家消費を軸に考えます。"),
        ("c-buy", "買い方（購入・リース・PPA）", "初期費用、所有権、保守の負担、契約期間が異なります。同じ設備でも、買い方で手元に残る金額の出方が変わります。"),
        ("c-maint", "保守・撤去・保証", "パワーコンディショナの更新、点検、将来の撤去費。長期の費用に含めて比較します。"),
    ],
    checks_lead="次があれば、条件別の試算ができます。そろっていなくても相談できます。",
    checks=["屋根の写真（できれば向きが分かるもの）と、おおよその面積・築年数・屋根材", "検針票12か月分（使用電力量と契約プラン）", "昼間の在宅状況と、昼間に使う設備（エコキュート・EV・エアコンなど）", "太陽光の有無（既設なら設置年・容量・売電単価）", "屋根の葺き替え・外壁塗装の予定", "購入・リース・PPAの希望と、初期費用の考え方"],
    checks_hint="屋根の面積が分からなくても、住所と屋根の写真から概略を確認できます。",
    paths_h2="解決策の分かれ道",
    paths_lead="導入する場合の買い方と、導入しない場合の代替を並べます。",
    paths=[
        ("主な解決策", "条件別シミュレーションで判断する", "屋根条件と検針票をもとに、自家消費率・売電・買い方を変えた複数のシナリオで回収の見通しを出します。固定の回収年数は示しません。", "<b>向く：</b>屋根が南〜東西向き、使用電力量が多い、昼間の使用がある<br><b>向かない：</b>北向き中心、面積が小さい、葺き替え予定", "#soudan", "屋根と検針票で採算の見通しを聞く", True),
        ("代わりの選択肢", "先に使い方を変える", "昼間の使用を増やす（エコキュートの昼間沸き上げ、家電の時間帯）、契約プランの見直しなど、設備を入れずにできることから始めます。", "<b>向く：</b>導入を急がない、初期費用を抑えたい<br><b>向かない：</b>すでに使い方を最適化している", "../ecocute/", "エコキュートの使い方と機種を見る", False),
        ("代わりの選択肢", "蓄電池・卒FITと合わせて考える", "既設の太陽光がある家や卒FITを迎える家は、蓄電池の要否と停電時の使い方を含めて比較します。", "<b>向く：</b>太陽光あり、停電の備えも考えたい<br><b>向かない：</b>太陽光なし", "../battery/", "蓄電池は必要か・停電で何時間", False),
    ],
    nogo="屋根が北向き中心、面積が小さい、数年内に葺き替え予定、昼間の使用が少なく売電に頼る計画になる場合は、導入を勧めません。回収年数を固定の数字で約束することもしません。試算の結果、導入しない方がよいと判断したら、そのままお伝えします。",
    costs_lead="設備価格だけでなく、長期の費用まで含めて比較します。",
    costs=[("容量と屋根条件", "設置できる容量、架台の種類、屋根材ごとの工法"), ("電気工事", "パワーコンディショナ、分電盤、系統連系の手続き"), ("買い方", "購入（初期費用あり）、リース、PPA（初期費用なし・契約期間あり）"), ("保守と更新", "定期点検、パワーコンディショナの更新時期"), ("撤去・保証", "将来の撤去費、機器保証・出力保証・工事保証の範囲"), ("補助制度", "国・県・市の制度は年度・予算で変わります。最新条件を確認してご案内します")],
    costs_note="金額は屋根条件と容量で変わるため、一律の価格は掲載していません。試算では前提条件を明記し、条件が変わればどう動くかも合わせてお伝えします。",
    faq=[
        ("結局、何年で元が取れますか", "屋根条件・使用電力量・昼間の使用・売電条件・買い方で大きく変わるため、固定の年数は断定しません。お宅の条件で複数のシナリオを試算し、前提とともにお伝えします。"),
        ("昼間に家にいなくても意味がありますか", "昼間の使用が少ないと自家消費率が下がり、売電に頼る形になります。エコキュートの昼間沸き上げや蓄電池で補う方法はありますが、費用が増えるため、試算のうえで判断します。導入しない方がよい場合もあります。"),
        ("リースやPPAと購入はどちらが得ですか", "一概には言えません。初期費用、所有権、保守負担、契約期間、契約後の扱いが異なります。同じ前提で並べて比較したうえで判断してください。"),
        ("補助金はありますか", "国・県・市の制度は年度・予算・要件で変わります。対象になり得るかは、設備と申請時期を確認したうえで最新条件をもとにご案内します。"),
    ],
    next=[("自分で確認する", "検針票12か月分の使用電力量と、屋根の向きを確認してください。昼間に家で使う電気が何かを書き出しておくと、自家消費の見通しが立ちます。"), ("家族で話す", "初期費用をかけるか、リースやPPAにするか、停電の備えも同時に考えるかを家族で共有しておくと、比較が早くなります。"), ("寺嵜と整理する", "屋根の写真と検針票をもとに、条件別の試算をお出しします。導入しない方がよい場合もそのままお伝えします。")],
    rel_evidence=[("よくあるご質問", "../../faq.html"), ("節約の虎の巻（電気・ガス代の考え方）", "../../column.html")],
    rel_kadai=[("卒FIT後どうするか", "../../sotsu-fit/"), ("蓄電池は必要か・停電で何時間", "../battery/"), ("エコキュートの交換・故障", "../ecocute/")],
    rel_back=[("住まいの困りごとから探す", "../#komarigoto"), ("お問い合わせ", "../../contact.html")],
))

# ---------- P0-4 住宅 3: 蓄電池は必要か／停電で何時間 ----------
PAGES.append(dict(
    file="residential/battery/index.html", photo_alt="分電盤と停電時に使いたい家電の実写", photo_caption="写真1 止めたくない機器と分電盤の回路から容量を決めます", path="/residential/battery/", rel="../../", audience="residential",
    title="蓄電池は本当に必要か 停電で何時間使えるかを先に計算｜千葉のご家庭｜シスコムサステナシールド",
    og_title="蓄電池は本当に必要か 停電で何時間使えるかを先に計算",
    desc="住宅用蓄電池の要否は、停電時に動かしたい機器・必要な電力量（kWh）・太陽光の有無・全負荷型か特定負荷型か・停電時の運用で決まります。必要kWhの目安計算つき。蓄電池を付けない選択肢も並べて比較。千葉県のご家庭向け。",
    crumbs=[("ホーム", "/"), ("住まいの困りごと", "/residential/"), ("蓄電池は必要か・停電で何時間", "/residential/battery/")],
    eyebrow="住まいの困りごと ｜ 蓄電池と停電",
    h1="<span class=\"l\">蓄電池は本当に必要か</span><br class=\"pc\"><span class=\"l accent\">停電で何時間使えるか</span> <span class=\"l\">先に計算</span>",
    lead="停電が不安だから蓄電池を、と考える前に、停電のときに何を何時間動かしたいかを決めると、必要な容量が見えてきます。太陽光の有無、全負荷型か特定負荷型か、停電時の運用まで確認すれば、蓄電池が要る家と要らない家に分かれます。付けない選択肢も一緒に並べます。",
    hero_meta="対応：<b>千葉県内の戸建て</b>（太陽光の有無を問わず相談できます）",
    cta_label="停電時に動かしたい機器から容量を聞く", cta_type="battery_need_check",
    cta_head="動かしたい機器と時間から 必要な容量を一緒に出します",
    cta_sub="蓄電池が要らない場合は、ポータブル電源や運用の工夫など、費用の小さい備えをお伝えします。",
    cta_note="相談は無料です。蓄電池の購入を前提にした営業はしません。",
    chips=[("停電で何時間もつか知りたい", "c-hours"), ("太陽光があるので検討中", "c-solar"), ("太陽光はないが停電が不安", "c-nosolar"), ("全負荷と特定負荷の違いが分からない", "c-type"), ("そもそも必要か迷っている", "c-need")],
    scene_h2="「停電が不安」の中身を 分けてみる",
    scene_body="<p>台風で丸一日停電した翌年、「蓄電池を付ければ安心」と見積を取った。金額を見て迷っているうちに、家族で話が食い違う。おじいさんは「冷蔵庫と照明があれば十分」、娘は「在宅勤務の通信と冷房が要る」。どこまで備えるかが決まっていないのに、容量だけが先に決まりかけていた。</p>",
    scene_view="見方を変える：停電のときに止めたくない機器を書き出し、消費電力と使う時間を掛け合わせると必要な電力量（kWh）が出ます。それが小さければ蓄電池でなくてもよく、大きければ太陽光との組み合わせや全負荷型を検討します。",
    causes_h2="要否を決める 5つの順番",
    causes_lead="上から順に決めると、容量と型が自然に絞られます。",
    causes=[
        ("c-need", "重要負荷を決める", "停電時に止めたくない機器。冷蔵庫・照明・通信・医療機器・給湯・冷暖房など。全部ではなく、優先順位をつけます。"),
        ("c-hours", "必要kWhを出す", "機器の消費電力（W）と使う時間（h）を掛け、合計します。下の目安計算で試せます。停電が何時間続く想定かも決めます。"),
        ("c-solar", "太陽光の有無", "太陽光があれば昼間に充電でき、長い停電でも使い続けられる可能性があります。なければ、貯めた分を使い切ったら終わりです。"),
        ("c-type", "全負荷型か特定負荷型か", "全負荷型は家全体に給電でき200V機器も使える製品がありますが費用が高め。特定負荷型はあらかじめ決めた回路だけに給電します。"),
        ("c-nosolar", "停電時の運用", "出力上限（同時に使える機器の合計）、切替の方法、夜間の使い方。容量が足りても出力が足りないことがあります。"),
    ],
    checks_lead="次を書き出しておくと、容量と型の判断が早くなります。",
    checks=["停電時に止めたくない機器と、その優先順位", "各機器の消費電力（本体のラベルや取扱説明書に記載）", "停電が何時間続く想定で備えるか", "太陽光の有無（設置年・容量・パワーコンディショナの自立運転の有無）", "分電盤の写真（回路数と200V回路の有無）", "医療機器など、絶対に止められないものの有無"],
    checks_hint="消費電力が分からない機器は、機種名を教えていただければ確認します。",
    paths_h2="解決策の分かれ道",
    paths_lead="必要kWhと太陽光の有無で、蓄電池・付けない選択肢・組み合わせに分かれます。",
    paths=[
        ("主な解決策", "必要kWhと太陽光の有無から容量と型を決める", "重要負荷と時間から必要kWhを出し、太陽光の有無で全負荷型・特定負荷型・容量を絞ります。停電時の出力上限と運用まで含めて選びます。", "<b>向く：</b>必要kWhが大きい、太陽光あり、長時間の停電に備えたい<br><b>向かない：</b>必要kWhが小さい、太陽光なしで数時間の備えで十分", "#soudan", "停電時に動かしたい機器から容量を聞く", True),
        ("代わりの選択肢", "蓄電池を付けない備え", "必要kWhが小さい場合。ポータブル電源、太陽光の自立運転コンセント、車のシガーソケット、情報と水の確保など、費用の小さい備えで足りることがあります。", "<b>向く：</b>冷蔵庫・照明・通信程度、停電が数時間の想定<br><b>向かない：</b>医療機器や冷暖房を長時間", "#soudan", "付けない場合の備え方を聞く", False),
        ("代わりの選択肢", "太陽光・卒FITと合わせて考える", "太陽光がある家や卒FITを迎える家は、昼間の余剰電力を貯める使い方と停電の備えを同時に比較できます。", "<b>向く：</b>太陽光あり、卒FIT前後<br><b>向かない：</b>太陽光なし", "../../sotsu-fit/", "卒FIT後の選択肢を比べる", False),
    ],
    nogo="必要kWhが小さく、停電が数時間の想定なら、蓄電池を勧めません。太陽光がない家で長時間の停電に備えたい場合も、貯めた分を使い切れば終わることをお伝えしたうえで、費用に見合うかを一緒に判断します。停電時の使用可能時間を固定の数字で約束することはありません。",
    costs_lead="蓄電池の費用は容量だけでは決まりません。",
    costs=[("容量（kWh）と出力（kW）", "貯められる量と、同時に使える機器の合計。どちらも要件に合わせます"), ("全負荷型か特定負荷型か", "家全体に給電するか、決めた回路だけか。切替盤の工事範囲が変わります"), ("太陽光との接続", "既設の太陽光と接続する場合、パワーコンディショナの型と保証の扱い"), ("設置場所と工事", "屋外か屋内か、基礎、配線距離、分電盤の改修"), ("保証と更新", "容量保証の年数と条件、将来の更新"), ("補助制度", "国・県・市の制度は年度・予算・要件で変わります。最新条件を確認してご案内します")],
    costs_note="金額は容量・型・工事条件で変わるため、一律の価格は掲載していません。試算では前提条件を明記します。",
    extra='''<section class="section" id="calc">
  <div class="wrap">
    <h2 class="h2">停電時に必要な電力量の 目安計算</h2>
    <p class="lead">止めたくない機器の消費電力（W）と使う時間（h）を入れると、必要な電力量（kWh）の合計が出ます。あくまで計算の目安で、実際に使える時間は製品の実効容量・出力上限・気温で変わります。</p>
    <div class="calc">
      <table>
        <thead><tr><th>機器</th><th>消費電力 W</th><th>使う時間 h</th><th>電力量 kWh</th></tr></thead>
        <tbody id="calcRows">
          <tr><td><input type="text" value="冷蔵庫" aria-label="機器1"></td><td><input type="number" class="w" value="" placeholder="例 100" min="0" aria-label="消費電力1"></td><td><input type="number" class="h" value="" placeholder="例 24" min="0" step="0.5" aria-label="時間1"></td><td class="kwh">0.00</td></tr>
          <tr><td><input type="text" value="照明" aria-label="機器2"></td><td><input type="number" class="w" value="" placeholder="例 40" min="0" aria-label="消費電力2"></td><td><input type="number" class="h" value="" placeholder="例 6" min="0" step="0.5" aria-label="時間2"></td><td class="kwh">0.00</td></tr>
          <tr><td><input type="text" value="通信・スマホ充電" aria-label="機器3"></td><td><input type="number" class="w" value="" placeholder="例 30" min="0" aria-label="消費電力3"></td><td><input type="number" class="h" value="" placeholder="例 24" min="0" step="0.5" aria-label="時間3"></td><td class="kwh">0.00</td></tr>
          <tr><td><input type="text" value="" placeholder="その他" aria-label="機器4"></td><td><input type="number" class="w" value="" placeholder="" min="0" aria-label="消費電力4"></td><td><input type="number" class="h" value="" placeholder="" min="0" step="0.5" aria-label="時間4"></td><td class="kwh">0.00</td></tr>
        </tbody>
      </table>
      <p class="result">合計の目安 <b id="calcTotal">0.00</b> kWh</p>
      <p class="note">消費電力は機器のラベルの値を入れてください。冷蔵庫やエアコンは運転状態で変動します。蓄電池は定格容量の全部を使えるわけではなく、同時に使える出力にも上限があります。この計算結果は入力した端末内でのみ処理され、送信されません。</p>
    </div>
    <script>
    (function(){
      var rows=document.querySelectorAll('#calcRows tr');var total=document.getElementById('calcTotal');
      function calc(){var sum=0;rows.forEach(function(r){var w=parseFloat(r.querySelector('.w').value)||0;var h=parseFloat(r.querySelector('.h').value)||0;var k=w*h/1000;r.querySelector('.kwh').textContent=k.toFixed(2);sum+=k;});total.textContent=sum.toFixed(2);}
      rows.forEach(function(r){r.querySelectorAll('input').forEach(function(i){i.addEventListener('input',calc);});});
    })();
    </script>
  </div>
</section>
''',
    faq=[
        ("停電で何時間使えますか", "動かす機器の合計消費電力と蓄電池の実効容量で決まり、太陽光があれば昼間に充電できる分が加わります。製品の定格容量をそのまま時間に換算せず、お宅の重要負荷で計算してお伝えします。固定の時間を約束することはありません。"),
        ("太陽光がなくても蓄電池は意味がありますか", "夜間に貯めて昼間に使う、停電に備えるという使い方はできますが、貯めた分を使い切れば終わりです。必要kWhが小さければ、蓄電池以外の備えで足りることもあります。"),
        ("全負荷型と特定負荷型はどちらがよいですか", "停電時に家全体で使いたいか、決めた回路だけでよいかで決まります。全負荷型は費用が高くなる傾向があり、特定負荷型は回路の選び方が重要です。重要負荷を決めてから選びます。"),
        ("補助金はありますか", "国・県・市の制度は年度・予算・要件で変わります。対象になり得るかは、機種と申請時期を確認したうえで最新条件をもとにご案内します。"),
    ],
    next=[("自分で確認する", "停電時に止めたくない機器を書き出し、上の目安計算で必要kWhを出してみてください。数が小さければ、蓄電池以外の備えで足りるかもしれません。"), ("家族で話す", "どこまで備えるか（冷蔵庫と照明だけか、冷暖房や通信までか）を家族で決めておくと、容量と型の判断が早くなります。"), ("寺嵜と整理する", "重要負荷と太陽光の有無をもとに、蓄電池が要るか、要るなら容量と型、要らないなら代わりの備えをお伝えします。")],
    rel_evidence=[("よくあるご質問", "../../faq.html"), ("卒FIT後の選択肢（蓄電池・エコキュート・V2H）", "../../sotsu-fit/")],
    rel_kadai=[("太陽光は元が取れるか", "../solar/"), ("エコキュートの交換・故障", "../ecocute/"), ("卒FIT後どうするか", "../../sotsu-fit/")],
    rel_back=[("住まいの困りごとから探す", "../#komarigoto"), ("お問い合わせ", "../../contact.html")],
))

# ============================================================
# P0-2 住宅HUB
# ============================================================
def residential_hub():
    p = dict(
        file="residential/index.html", path="/residential/", rel="../", audience="residential",
        title="住まいの困りごとから探す 暑さ寒さ・電気代・設備・停電の相談窓口｜千葉｜シスコムサステナシールド",
        og_title="住まいの困りごとから探す 暑さ寒さ・電気代・設備・停電の相談窓口",
        desc="千葉県のご家庭向け。電気代が高い、お湯・給湯器が心配、停電が不安、卒FIT後どうするか、2階が暑い、太陽光は元が取れるか、屋根・外壁を先に直すべきか、見積が適正か。8つの困りごとから、原因・解決策・まず確認するものへ進めます。不要なら不要と言います。",
        crumbs=[("ホーム", "/"), ("住まいの困りごと", "/residential/")],
        faq=[
            ("相談すると営業されますか", "相談・確認は無料で、訪問販売や即決を求める営業はしません。確認した結果、今は何もしないのが最善なら、そうお伝えします。"),
            ("どの困りごとか分からないのですが", "困りごとを選ばなくても相談できます。今の暮らしで気になっていることを、そのままお聞かせください。"),
            ("千葉県以外でも相談できますか", "千葉県内のご家庭を中心に対応しています。県外の場合は内容によりますので、まずご相談ください。"),
        ],
    )
    cards = [
        ("電気代が高い", "給湯・冷暖房・契約プラン・使い方のどれかに偏りがあります", "契約の見直し、給湯器の見直し、太陽光の自家消費", "検針票12か月分と、給湯器の種類", "../column.html", "電気・ガス代の見方を読む"),
        ("お湯・給湯器が心配", "使用年数、エラー、湯量不足、設置場所の条件", "修理・設定変更、通常型かおひさま型への交換", "エラー番号、型式と製造年、設置場所の写真3枚", "ecocute/", "直すか替えるかを整理する"),
        ("停電が不安", "止めたくない機器と必要な電力量が決まっていない", "蓄電池、太陽光の自立運転、付けない備え", "停電時に止めたくない機器と、その消費電力", "battery/", "停電で何時間使えるかを計算する"),
        ("卒FIT後どうするか", "売電単価が下がり、売るより使う方が価値が出やすい", "売電継続、自家消費、蓄電池、エコキュートの昼間沸き上げ", "年間発電量、自家消費量、給湯器の種類", "../sotsu-fit/", "4つの選択肢を比べる"),
        ("2階が暑い エアコンが効かない", "屋根の熱、窓からの日射、断熱不足、エアコンの能力", "窓の遮熱、屋根の遮熱、エアコンの運転と機種の見直し", "午後の2階と1階の温度差、窓の向き", "../contact.html", "状況を伝えて対策の順番を聞く"),
        ("太陽光は元が取れるか", "屋根条件、使用電力量、昼間の使用、売電条件、買い方", "条件別の試算、先に使い方を変える、蓄電池との組み合わせ", "屋根の写真と検針票12か月分", "solar/", "条件別の見通しを聞く"),
        ("屋根・外壁を先に直すべきか", "築年、塗膜の劣化、雨漏り、錆。太陽光より先に直す場合があります", "補修、遮熱塗装、長期耐候のコーティング", "築年数、前回の塗装時期、雨漏りの跡", "../lp/#triple-guard", "屋根・外壁のコーティングを見る"),
        ("見積が適正か 本当に必要な設備か", "内訳が分かれていない、前提が違う見積を比べている", "内訳をそろえて比較、不要なら不要と伝える", "見積書（本体・工事・撤去・諸経費の内訳）", "../contact.html", "見積を持って相談する"),
    ]
    cards_html = ""
    for i, (h, cause, sol, chk, href, label) in enumerate(cards):
        cards_html += f'''<a class="kadai-card" href="{href}">
        <div class="num">0{i+1}</div>
        <h3>{esc(h)}</h3>
        <dl><dt>考えられる原因</dt><dd>{esc(cause)}</dd><dt>主な解決策</dt><dd>{esc(sol)}</dd><dt>まず確認するもの</dt><dd>{esc(chk)}</dd></dl>
        <span class="go">{esc(label)}</span>
      </a>'''
    faqs = "".join(f'<div class="faq-item"><h3>{esc(q)}</h3><p>{esc(a)}</p></div>' for q, a in p["faq"])
    body = f'''<section class="hero">
  <div class="hero-inner">
    <div>
      <div class="eyebrow">千葉のご家庭へ ｜ 住まいの困りごと</div>
      <h1><span class="l">家族で違う「気になる」を</span><br class="pc"><span class="l accent">住まいの相談から</span> <span class="l">一緒に整理</span></h1>
      <p class="lead">暑さ寒さ 電気代 設備の交換 停電への備え。今の暮らしで気になっていることからお聞かせください。商品を選ぶ前に、困りごとから入れるようにしました。答えなくても、給湯器・エコキュートのサービスや相談窓口へ直接進めます。</p>
      <div class="hero-cta">
        <a class="btn btn-gold" href="#komarigoto">困りごとから探す</a>
        <a class="btn btn-ghost" href="../service.html">サービスと価格の考え方を見る</a>
      </div>
      <div class="hero-meta">対応：<b>千葉県内のご家庭</b> ｜ 相談は無料 ｜ 今すぐ工事を頼みたい方は <a href="../contact.html" style="text-decoration:underline">お問い合わせ</a> へ</div>
    </div>
    <div>
      {hero_figure("residential/index.html", "../", "千葉の戸建て住宅と家族", "架空の施工実績や口コミは載せません")}
    </div>
  </div>
</section>

<section class="section alt first" id="komarigoto">
  <div class="wrap">
    <h2 class="h2">あなたの場合は どれに近いですか</h2>
    <p class="lead">8つの困りごとから選ぶと、考えられる原因・主な解決策・まず確認するものと、次に読むページへ進みます。</p>
    <div class="kadai-grid">{cards_html}</div>
    <p class="note">どれにも当てはまらない場合や、複数が重なる場合は、そのまま <a href="../contact.html">お問い合わせ</a> からお聞かせください。</p>
  </div>
</section>

{trust_block("residential")}

<section class="section" id="soudan-hub">
  <div class="wrap">
    <h2 class="h2">何を選ぶかより 何から始めるかを一緒に整理します</h2>
    <div class="cta-box">
      <div class="face"><img src="../assets/terasaki-profile.jpg" alt="代表 寺嵜忠弘"></div>
      <div>
        <div class="who">代表 寺嵜忠弘 ｜ 電気業界27年 ｜ 千葉拠点</div>
        <h3>高い設備から勧めることはありません</h3>
        <p>家全体の状態と電気の使い方を見て、最初に手をつける場所から整理します。必要のない工事は必要ないとお伝えします。</p>
        <div class="btns"><a class="btn btn-gold" href="../contact.html" data-event="cta_click" data-cta-type="hub_consult" data-cta-position="hub">相談する</a><a class="btn btn-ghost" href="../contact.html">写真を送って見てもらう</a></div>
        <p class="tel">お電話でも承ります <a href="{TEL}">{TEL_DISP}</a></p>
      </div>
    </div>
  </div>
</section>

<section class="section alt" id="direct">
  <div class="wrap">
    <h2 class="h2">困りごとを選ばずに 進みたい方へ</h2>
    <p class="lead">すでに何をしたいか決まっている方は、こちらから直接進めます。</p>
    <div class="related-grid">
      <div class="related-col"><h4>サービスと価格の考え方</h4><ul>
        <li><a href="../service.html">プロパンガス切替・給湯器・エコキュート</a></li>
        <li><a href="../flow.html">ご利用の流れ</a></li>
        <li><a href="../voice.html">お客様の声</a></li>
      </ul></div>
      <div class="related-col"><h4>読みもの・診断</h4><ul>
        <li><a href="../column.html">節約の虎の巻（電気・ガス・給湯器）</a></li>
        <li><a href="../shindan.html">ガス代のかんたん診断</a></li>
        <li><a href="../faq.html">よくあるご質問</a></li>
      </ul></div>
      <div class="related-col"><h4>相談する</h4><ul>
        <li><a href="../contact.html">お問い合わせフォーム</a></li>
        <li><a href="{TEL}">電話 {TEL_DISP}</a></li>
        <li><a href="../">法人・事業所の方はこちら</a></li>
      </ul></div>
    </div>
  </div>
</section>

<section class="section" id="faq">
  <div class="wrap">
    <h2 class="h2">よくあるご質問</h2>
    {faqs}
  </div>
</section>
'''
    return p, add_en_labels(head(p) + header(p) + body + footer(p))

def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", path, len(content.encode("utf-8")), "bytes")

for p in PAGES:
    write(p["file"], kadai_page(p))
p, h = residential_hub()
write(p["file"], h)
