# 新生社様 提案書 (5プラン版・音声修正版)

## 同梱物
- index.html  メイン(画像埋め込み・1ファイルで動く)
- index_slides版.html  軽量版
- shinseisha_proposal.pdf  ダウンロードリンク用PDF (必須)
- 新生社様_省エネ創エネダブルプラン提案書.pdf / .pptx
- slides/slide-01.jpg〜20.jpg
- build_pptx.js

## 今回の音声修正
- 句読点(、)でも文を分割 (1文の長さを短く)
- 50文字超は強制分割 (iOS Safari対策)
- 各chunk前にspeechSynthesis.cancel()でキューリセット
- speak前60ms遅延 (cancel→speak連続失敗回避)
- onend不発時のタイムアウト保険5秒
- PC Chrome自動再生制限対策

## ブラウザ対応
- Chrome / Edge / Safari (Mac/iPhone/iPad) / Firefox = OK
- IE = 非対応 (2022年6月Microsoft公式サポート終了。Edgeに自動移行されます)
- IEユーザー向けには「PDFダウンロード」リンクを案内

## アップ手順
1. GitHub Desktop で syscomnet-proposals-public リポジトリ
2. shinseisha フォルダごと上書きコピー
3. Commit → Push origin
4. 1〜3分後に公開URL反映

公開URL: https://t-terasaki-beep.github.io/syscomnet-proposals-public/shinseisha/

作成: シスコムサステナシールド 寺嵜忠弘 / 2026年5月
