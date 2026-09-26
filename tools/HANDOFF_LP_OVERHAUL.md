# 引き継ぎ｜サステナシールド全LP改修 P0（2026-09-26）

## 正本
- Notion「【9/21月20時JST以降着手】サステナシールド全LP｜気づきと対話を生む全面改修」（Web実装キュー）
  https://app.notion.com/p/3dc81978cf7881c2b147c4e9b4d37226 ステータス＝テスト中／L3承認待ち
- 表現ガイド: 正七角形 表現ガイド v1.0（見出しは守る対象から／「必要ありません」ブロック必須／禁止表現）
- 配色正本: R1 Web全面改修（2026-08-21 寺嵜承認）白基調70%以上・スカイブルー#00AEEFは罫のみ・本文#102F40

## 成果物
- GitHub draft PR #8 https://github.com/t-terasaki-beep/syscom-sustainashield/pull/8（branch claude/sustainashield-lp-overhaul-s52zmg）
- 新規: residential/（住宅HUB）, business/atsui/ denkidai/ cubicle/, residential/ecocute/ solar/ battery/, assets/kadai.css, assets/terasaki-profile.jpg
- 変更: index.html（法人HUB 困りごと入口8件＋約束＋寺嵜ブロック）, sotsu-fit/（卒FIT 4選択肢比較）, shanetsu-chiba/ と lp/（関連課題リンク）
- 生成元: tools/gen_pages.py（課題LP6ページ＋住宅HUBの文言・構成の正本。編集後に `python3 tools/gen_pages.py .` で再生成）

## デザインの変遷（寺嵜フィードバック）
1. 紺グラデ＋ゴールドのテンプレ型 → 「こういう感じではない」
2. 紙色・紺ベタの3案（現場ノート／相談カウンター／特集記事） → 「湿っぽい」
3. R1配色（白・スカイブルー罫・オレンジCTA・Noto Sans JP） → 「フォントが今一・AIっぽい」
4. 明朝見出し（Shippori Mincho B1）＋Zen Kaku Gothic New本文、ラベル反復と矢印撤去 → 「オレンジCTAはやめたい」
5. CTAを濃紺 #102F40 に変更（現在のPR状態、commit e62da32）。ゴールド/深緑の比較画像も提示済み、未決
6. 参考サイト提示: https://vivid-grp.co.jp/ 「今時・明るい・スマホ版を見習え」
   → 「明るい・今時」試作を assets/kadai-bright.css（上書きCSS、未適用）として作成。太いゴシック・角丸カード・淡水色の交互背景・丸ボタン・画面下固定バー

## 未決・次にやること
1. vivid-grp.co.jp の実物確認。このコンテナはネットワーク拒否だったため、子セッション session_01DoGtJVzwQ3ynpMu3RJBJR9 に調査を依頼済み。get_session / list_events で結果を回収する（新規コンテナは許可ドメインが効く想定）
2. 調査結果を基に「再更新候補」を提示 → 採用されたら assets/kadai-bright.css の方向で kadai.css を書き換え、tools/gen_pages.py を調整して再生成、index.html の .kd-* も揃える
3. CTA色の確定（濃紺／ゴールド／深緑／vivid準拠）
4. 実写写真の配置（寺嵜決定・許諾済みのみ）
5. 公開手段の確定（GitHub Pages へマージ／名前.com へ手動配置、後者は本番原本の突合が先）。本番公開はL3

## 検査の型
- 375px/1280px 横スクロール0、内部リンク・画像切れ0、見出し行数 PC2行・スマホ2〜3行、各課題LPに LINE1・電話1・フォーム3〜4
- Google Fonts はコンテナから遮断される。tools/preview/fontroute.js で @fontsource を差し込んで描画する

## 制約（FACT）
- 本番 syscom-sustaina-shield.com、メーカー・競合7サイト、Notion画像アップロード(api.notion.com) は cloud から到達不可
- 数値・実績・価格・補助額・削減率は新規に断定しない。会話は「例えばこんな場面」と明示
