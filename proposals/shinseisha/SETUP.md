# 新生社様提案書 公開セットアップ手順

寺嵜社長へ

Claudeが `index.html` と `README.md` を自動配置しました。
あとは画像とPDFを配置するだけで完了です。

## 残りの手順（所要 約3分）

### STEP 1: 画像とPDFを配置

1. ダウンロードフォルダから `shinseisha-assets.zip` を見つける
   （まだない場合：Claudeのチャット下部からダウンロード）

2. zipを **このフォルダ内で解凍** する：
   `C:\Users\terasaki\Documents\GitHub\syscom-sustainashield\proposals\shinseisha\`

3. 解凍後、フォルダ構造が以下のようになっていればOK：

```
proposals/shinseisha/
├── index.html
├── README.md
├── SETUP.md (このファイル)
├── shinseisha_proposal.pdf
└── slides/
    ├── slide-01.jpg
    ├── slide-02.jpg
    ├── ...
    └── slide-17.jpg
```

### STEP 2: ローカルで動作確認

`index.html` をダブルクリックでブラウザで開いて、
- スライドが表示される
- 自動再生でナレーションが流れる
- PDFダウンロードボタンが動く
が確認できれば成功です。

### STEP 3: GitHubへPush

GitHub Desktopを起動して：

1. シスコムサステナシールドのリポジトリを開く
2. 左側に変更ファイル一覧が表示される
   - `proposals/shinseisha/index.html` (新規)
   - `proposals/shinseisha/README.md` (新規)
   - `proposals/shinseisha/SETUP.md` (新規)
   - `proposals/shinseisha/shinseisha_proposal.pdf` (新規)
   - `proposals/shinseisha/slides/slide-01.jpg〜17.jpg` (新規)
3. 左下の "Summary" に：
   `新生社様 省エネ・創エネ ダブルプラン提案書を追加`
4. "Commit to main" → "Push origin"

### STEP 4: 公開URL確認

数分後、以下のURLでアクセス可能：

```
https://[GitHubユーザー名].github.io/syscom-sustainashield/proposals/shinseisha/
```

GitHub Pages が未設定の場合：
リポジトリ Settings → Pages → Source: main / root → Save

### STEP 5: LINEで新生社様へ送信

```
新生社 田所様

先日お話ししました省エネ・創エネ ダブルプランの
ご提案書、スマホで見られる形でお送りします。

▼ご提案ページ
https://[ユーザー名].github.io/syscom-sustainashield/proposals/shinseisha/

【見どころ】
・「自動再生」ボタンで音声ナレーション付き再生
・約8分で全体像をご確認いただけます  
・脂肪族ポリウレアの公式解説動画(4本)も最後にあります
・PDF版も同ページからダウンロードできます

20年累計でA案より2,976万円お得、
千葉県補助金で960万円を取り戻せる試算になっています。

ご質問・現地調査のご希望は、いつでもこのLINEで
お気軽にどうぞ。

株式会社シスコムネット 特販営業部
寺嵜 忠弘
建設業許可：千葉県知事 (般-2) 第46651号
```

---

## 困ったときは

- LINEで「Claudeに相談」→画面のスクリーンショット送付で即時対応
- GitHub Pagesが反映されない → 5分待つ、ブラウザのキャッシュクリア
- スライド画像が表示されない → zipの解凍場所を再確認

© 2026 シスコムサステナシールド
