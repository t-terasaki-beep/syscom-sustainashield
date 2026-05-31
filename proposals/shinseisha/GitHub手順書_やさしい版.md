# 新生社様 提案書 v8版 (塗装暑さ対策ならず・5プラン完成版)

## 同梱物
- **index.html** メイン: 画像埋込+MP3外部参照 (約5.3MB)
- index_slides版.html 軽量版(画像も外部参照)
- shinseisha_proposal.pdf ダウンロードリンク用PDF
- 新生社様_省エネ創エネダブルプラン提案書.pdf / .pptx
- **slides/** スライド画像20枚 (新数値版)
- **mp3/** ナレーション音声20本 (v8新台本版 5.7MB)
- build_pptx.js

## v8の主な変更
- A/B/C案メンテ: 2,439万 → **6,584万円** (塗装+全面足場+物価高騰込)
- D案 A比: ▲2,724 → **▲6,869万円**
- E案 A比: ▲4,004 → **▲8,149万円 (最安)**
- E案来年外壁: 全面足場540万を含む1,860万→補助▲930→実質930万
- **★スライド13に「塗装は暑さ対策にならない」メッセージ全面強調**
- 音声・ページ送りロジック堅牢化:
  - MP3外部参照化(base64廃止)で audio.duration 正確取得
  - ended イベント唯一トリガー化で「読み終える前に進む」を防止
  - stopAudio強化で「ページ変わると止まる」を防止

## アップ手順
1. GitHub Desktop で syscom-sustainashield リポジトリ
2. proposals/shinseisha/ フォルダごと中身上書き
3. Commit → Push

公開URL: https://t-terasaki-beep.github.io/syscom-sustainashield/proposals/shinseisha/
