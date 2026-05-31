# 新生社様 提案書 (5プラン版・MP3音声埋め込み版)

## 同梱物
- **index.html** メイン: 画像・音声すべて埋め込んだ完全1ファイル版 (約13MB)
  → どのブラウザでも確実に動きます
- index_slides版.html 軽量版 (音声は埋込・画像は外部参照)
- shinseisha_proposal.pdf ダウンロードリンク用PDF
- 新生社様_省エネ創エネダブルプラン提案書.pdf / .pptx
- slides/ 各ページ画像 (20枚)
- mp3/ ナレーション音声 (20本)
- build_pptx.js

## 今回の大きな変更
- **音声合成APIをやめてMP3音声に切り替え**
- Microsoft Edge TTS の日本語音声「Nanami(女性)」で全20本を事前生成
- Brave・iPhone Safari・PC Chrome・Edge・どのブラウザでも自動再生&自動ページ送りが確実に動作
- 音質も合成より大幅に自然

## アップ手順
1. GitHub Desktop で syscomnet-proposals-public リポジトリ
2. shinseisha フォルダごと上書き
3. Commit → Push

公開URL: https://t-terasaki-beep.github.io/syscomnet-proposals-public/shinseisha/

## ナレーション差し替え方法
mp3gen フォルダの gen_mp3.py を編集してテキストを変えれば、
edge-tts で新しいMP3を再生成できます。

作成: シスコムサステナシールド 寺嵜忠弘 / 2026年5月
