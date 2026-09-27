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
1. vivid-grp.co.jp の実物確認。このコンテナは拒否。新規に起動した子セッション session_01DoGtJVzwQ3ynpMu3RJBJR9 でも「proxy blocks port 443」で拒否（2026-09-26 12:06 UTC）。寺嵜は「許可した」と言っているが、環境 env_01GM5u1MEpPzSN7ASdp4WH9y の Network access に反映されていない可能性が高い。次セッションではまず curl で到達確認し、駄目なら環境設定の再確認かスクリーンショット提供を依頼する
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

---
# 追記 2026-09-26（cloud session_01DoGtJVzwQ3ynpMu3RJBJR9）｜vivid準拠デザインを本体化（kadai.css v2）

## この回でできたこと（FACT）
- 新規コンテナから vivid-grp.co.jp と本番 syscom-sustaina-shield.com の両方に到達できた（curl 200／Chromium 描画 OK）
- 本番の全98ページ（sitemap 80件＋既知URL）を取得しSHA256を記録：`/home/user/sustaina-backup/prod_20260926T141243Z/`（このセッションのコンテナ内。寺嵜PC側にも同じ手順で取得すること）
- vivid-grp.co.jp を 390px で実測。値は Notion「サステナシールド全LP｜気づきと対話を生む全面改修」2026-09-26 追記と本セッション報告に記録
- `assets/kadai.css` を vivid 実測値ベースで全面書き換え（旧版は `assets/kadai-r1.css` に保持）。`assets/kadai-bright.css` は役目を終えたので参考のみ
- `tools/gen_pages.py`：FONTS を Noto Sans JP＋Montserrat に変更、ハンバーガー＋ドロワー、画面下固定バー（相談する｜LINEで送る）、セクション英字ラベル（EN_LABELS）を追加し 7 ページを再生成
- `index.html`（法人HUB）は kd-* 区画のみ同じ見え方へ（帯＋白カード＋丸ボタン）。ヘッダー・写真ヒーロー・その他の旧セクションは触っていない
- 検査：11ページ 390px／1280px 横スクロール 0、JSエラー 0、読込失敗 0。既存の `.hero-overlay-sun`（index）と `.kpi-box`（/lp/）の右はみ出しは本件以前からのもので今回未修正

## デザインの値（kadai.css v2）
- 地色 白／帯 #E8F7FD（白と交互）／カード内淡色 #F3FBFE／罫 #D9E8EF
- アクセント スカイ #00AEEF・#0093CF（見出し短罫 30×3、英字ラベル、番号、リンク、カード見出しの左罫）
- CTA `--cta` 1色。既定＝濃紺 #102F40。`html[data-cta="sky"]`＝#0093CF、`html[data-cta="coral"]`＝#FA7748（vivid値）、`html[data-accent="teal"]`＝アクセントを vivid の #38B3D0 系へ
- 書体 Noto Sans JP 本文400・見出し700／Montserrat 600-700（英字ラベル・番号・電話番号）
- 角丸 カード20px・相談ブロック24px・ボタン999（高さ SP52px／PC60px、右端矢印）。影・グラデーション・絵文字なし
- スマホ：ヘッダー白 sticky 64px＋ハンバーガー（右からドロワー）、下部固定バー 56px 2分割（相談する＝--cta／LINEで送る＝#06C755）

## 未決（寺嵜判断）
1. CTA色：A 濃紺（既定）／B スカイ／C コーラル（vivid値）。比較画像は `sustaina-lp-review/compare.html`
2. アクセントを R1 の #00AEEF のままにするか、vivid の #38B3D0 に寄せるか（D案）
3. R1 配色正本「スカイブルーは罫のみ・淡色ベタ塗り禁止」と本案（淡水色帯・スカイ塗りの英字ラベル）の矛盾 → 採用時は R1 改訂として記録
4. 法人HUB index.html のヘッダー・ヒーロー・旧セクションを同じ型に揃えるか（別作業・大きい）

## 検査スクリプト
Google Fonts が到達できる環境では `tools/preview/fontroute.js` は不要（差し込むと @fontsource 未導入のためフォントが落ちる）。到達できない環境のみ使う。

---

## 2026-09-27 追記（寺嵜PCローカルセッション）
- **CTA色＝スカイで確定**（寺嵜決定）。assets/kadai.css と公開パッケージ ss-bright-v1.css の既定を #0093CF／hover #0079AD に変更。濃紺は `data-cta="navy"`、コーラルは `data-cta="coral"` で切替。法人HUB index.html の寺嵜ブロック主ボタン（直書き濃紺）もスカイへ。公開パッケージの SHA256SUMS は css 分を更新済み
- **ヒーロー写真7枠を配置**（寺嵜指示：本番掲載済みの写真を流用、足りない分は ChatGPT で生成）
  - 本番流用5枚：工場・倉庫が暑い＝/images/coating.jpg、住宅HUB＝oh01-ohisama-hero-v2、エコキュート＝ec01-ecocute-hero-v2、太陽光＝/residential/solar/assets/hero-solar.jpg、蓄電池＝b01-annual-data-three-destinations-v2
  - ChatGPT 生成2枚（2026-09-27）：電気代・デマンド＝office-demand.jpg、キュービクル＝cubicle-check.jpg
  - 保存先 assets/photos/。割り当ては tools/gen_pages.py の HERO_PHOTOS。どれも実際の施工・測定写真ではないので、キャプション先頭に「写真はイメージです。」、alt に「（イメージ）」を自動付与。実写が手に入ったら HERO_PHOTOS の差し替えだけで済む
- 検査：11ページ×390/1280px 横スクロール0・JSエラー0・読込失敗0・写真プレースホルダー残0
- 注意：白文字×#0093CF のコントラスト比は約3.5で、WCAG AA（本文4.5）に届かない。ボタン文字は太字15〜16px。気になる場合は既定を #0079AD（約4.8）に一段濃くする

---

## 2026-09-27 20:09 JST 本番公開済み（寺嵜L3承認）
- 本番はお名前.com（nginx）。GitHub Pages ではないので、PR マージでは公開されない。公開は FTP で、寺嵜さんが実行時にパスワードを入力するスクリプトを使った
- 公開物・原本バックアップ・検査・戻し手順：`Desktop/_run/DEPLOY_LP_20260927/`（build_upload.py → upload/、qa_staging.js、publish.ps1 -Mode publish|rollback）
- 公開した16ファイル：住宅9ページ＋/assets/ss-bright-v1.css（本番原本に1行追加）、新規 /business/cubicle/＋kadai.css・terasaki-profile.jpg・photos/cubicle-check.jpg、トップ「詳しい解説ページ」欄にキュービクルのカード、sitemap に1件
- 公開しなかったもの：/business/atsui/・/business/denkidai/（本番の /business/roof-heat/・/energy-cost-reduction/ と検索意図が重なる）、PR の法人HUB・遮熱・/lp/・住宅HUB等の HTML（本番が別デザインで新しい）
- 公開後の本番検査：11ページ×390/1280px 横スクロール0・JSエラー0・内部リンク切れ0
- 既存不具合：/api/approved-cases.php が 500（公開前から）
- 次：①事例APIの500 ②atsui/denkidai の中身を既存ページへ追記 ③7日後の相談件数比較 ④FTPパスワード変更
