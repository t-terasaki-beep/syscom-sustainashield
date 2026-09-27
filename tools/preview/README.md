# プレビュー・検査スクリプト（ローカル用）

前提: `python3 -m http.server 8765 --directory <repo_root>` を起動しておく。
Playwright はグローバル（`NODE_PATH=/opt/node22/lib/node_modules`）、Chromium は `/opt/pw-browsers/chromium`。

- `shot.js` 全11ページを375px/1280pxで撮影し、横スクロール・リンク切れ・LINE/電話/フォーム本数を出す
- `heroes.js` 8見出しの行数・文字サイズを実測（PC2行／スマホ2〜3行の検査）
- `fontroute.js` Google Fonts が遮断された環境で、`@fontsource`（npm）の同じ書体を差し込むルート。`npm i @fontsource/shippori-mincho-b1 @fontsource/zen-kaku-gothic-new @fontsource/noto-serif-jp` を `pw/` 配下に入れて使う
- `bright.js` `assets/kadai-bright.css`（「明るい・今時」試作の上書きCSS）を当てて撮影
- `variants.js` CTA色（濃紺／ゴールド／深緑）の比較撮影
