# 住宅ページ「明るい・今時」上書きレイヤー 公開パッケージ v1（2026-09-26）

状態：READY FOR APPROVAL（L3・寺嵜承認後に公開）。本番は未変更。

## 何を変えるか
- 新規ファイル 1 つ：`/assets/ss-bright-v1.css`
- 既存 HTML 9 ページ：`</head>` の直前に 1 行追加するだけ
  `<link rel="stylesheet" href="/assets/ss-bright-v1.css?v=1">`
- 本文・文言・画像・計測タグ・LINE／電話リンクは一切変更しない（changes.diff の追加行は 9 行のみ）

| 対象ページ |
|---|
| /residential/ |
| /residential/ecocute/ |
| /residential/solar/ |
| /residential/battery/ |
| /residential/sotsu-fit/ |
| /residential/ohisama/ |
| /residential/guide/ohisama/ |
| /residential/roof-wall/ |
| /residential/window/ |

HTML は 2026-09-26 14:12 UTC に取得した本番原本に 1 行足したもの。公開直前に本番が更新されていないか SHA256 を照合すること（原本の値は prod バックアップの SHA256SUMS.txt）。

## 公開手順（お名前.com FTP）
1. 公開直前に本番 9 ページを再取得し、バックアップの SHA256 と一致するか確認。違えば、その最新版に同じ 1 行を足して作り直す
2. `assets/ss-bright-v1.css` を `public_html/assets/` にアップロード
3. `residential/…/index.html` 9 ファイルを同じパスへ上書きアップロード
4. スマホとPCで 9 ページを開き、帯が淡い水色・ボタンが丸いこと、電話・LINE・寺嵜AIボタンが動くことを確認

## 戻し手順（どれか 1 つで戻る）
- 最速：`public_html/assets/ss-bright-v1.css` の中身を空にして上書き（HTML はそのままで見た目が元に戻る）
- 完全：バックアップの原本 9 ファイルを同じパスへ上書きし、css を削除

## 戻す判断基準
- 表示崩れの報告が 1 件でも出た
- 公開後 7 日間の住宅ページ経由の相談（LINE・フォーム・電話）が、直前 7 日間より明らかに減った

## CTA 色の切替
既定は濃紺 #102F40。html 要素に `data-cta="sky"`（#0093CF）または `data-cta="coral"`（#FA7748）を付けると切り替わる。CSS 変数 `--ssb-cta` を書き換えても同じ。
