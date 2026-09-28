# LP共通「資料・動画セット」v1（2026-09-28）

寺嵜指示（2026-09-28）：「各LPには、資料ダウンロードと、スケッチ商材ならスケッチ商材のPDF、YouTubeをセットで表示してほしい」「資料ダウンロードのページが消えたように思える」

## 何が入るか
各LPの共通フッターの直前に、1ブロック（`<!-- ss-media-set:v1 -->`〜`<!-- /ss-media-set:v1 -->`）を入れる。

| 枠 | 中身 |
|---|---|
| YouTube 2本 | ページのテーマに合う TERAちゃんねるの解説動画。押すまでサムネ画像だけ出し、表示を重くしない（youtube-nocookie） |
| 資料 | 「資料ダウンロードへ」ボタン（/download/）。スケッチ商材のページは **スケッチ商材資料** のラベルとPDF名を出し、/download/ で該当資料にチェックが入った状態で開く |
| 動画一覧 | 「テーマ別の解説動画をすべて見る」→ 新規 /videos/（15本をテーマ別に並べた一覧） |
| コラム | 「寺嵜のコラムを読む」→ 新規 /column/（寺嵜提示モック準拠：ヒーロー・カテゴリ絞り込み・3列カード・検索・新着・相談CTA。写真は column/img/ に同梱、すべてイメージ）（Notion 📝 note記事DB のうち note公開済み6本。公開待ち12・レビュー6は個別承認前のため載せない） |

ページ→テーマ→動画・資料の割り当ては `media-map.json` が正本。URLの前方一致で、長いものが優先。

| テーマ | 主なURL | 動画 | 資料 |
|---|---|---|---|
| 屋根・外壁の遮熱 | /shanetsu-chiba/ /factory-roof-heat-chiba/ /business/roof-heat/ /atsusa-taisaku-chiba/ /residential/roof-wall/ | 冷暖トリプルガードコート／夏の2階が暑い | スケッチ：トリプルガードコート説明資料 |
| 特殊コーティング | /business/special-coating/ /business/special/ | トリプルガードコート／UVシールドPu | スケッチ |
| 窓の遮熱 | /residential/window/ /atsusa-taisaku-chiba/nishibi/ | 窓ガラスコーティング／窓ぎわの暑さ | 会社・サービス案内 |
| エコキュート | /residential/ecocute/ ohisama/ chiba-blackout/ /ecocute-chiba/ | エコキュート交換／おひさまエコキュート | 同上 |
| 太陽光・蓄電池・停電 | /residential/solar/ battery/ /taiyoko-chiba/ /teiden-taisaku-chiba/ /business/bcp/ | 太陽光／太陽光＋蓄電池＋BCP | 同上 |
| 卒FIT | /sotsu-fit/ /sotsufit-chiba/ | 卒FIT 2本 | 同上 |
| 補助金・電気代・キュービクル・害虫・その他 | media-map.json 参照 | | |

入れないページ：noindex、/download/ /videos/ /contact /privacy /tokushoho /company /faq /flow、/proposals/（顧客名入り）、/design-vis/、千葉エネルギー研究会（別ブランド）、旧コピー（/public_html/ /residential2026.09.19/）。

## スケッチ資料を直リンクにしない理由（FACT）
Drive の「防さび、防水、断熱シールド.pdf」（スケッチ製、2024-02）には **2024年時点の材工単価（1㎡6,000円税別）** と **「業界NO.1」** の表記がある。直リンクで公開すると当社サイトの断定表示になるため、/download/ のフォームで請求を受け、送付時に「価格は資料作成時点のメーカー記載・現在は個別見積」を添えて寺嵜から送る。請求はそのまま見込み客リストになる。
「冷暖ガラスシールドって何（加盟店向け資料）」・材料コスト比較・注文書は **加盟店向けなので載せない**。MSDS（安全データシート）は求められたら個別送付。

## 手順（寺嵜PC・本番ミラーがある環境）
```powershell
# 1. 本番を取り直した最新ミラーで DryRun（何ページに何が入るか _report/changes.csv で確認）
python tools/publish/lp-media-set-v1/inject.py --site <本番ミラー> --out Desktop/_run/DEPLOY_MEDIASET_v1
# 2. 公開物を作る（本番ミラーは書き換えない。変わるファイルだけが --out に出る）
python tools/publish/lp-media-set-v1/inject.py --site <本番ミラー> --out Desktop/_run/DEPLOY_MEDIASET_v1 --apply --replace-download
# 3. 390px／1280px で横はみ出し0・JSエラー0・リンク切れ0 を確認 → 既存の publish.ps1 と同じ方式で公開・再取得して SHA256 照合
# 4. YouTube に届く環境で動画の公開状態を確認（非公開・削除が混ざっていないか）
python ../terasaki-os-code/tools/line_richmenu_tera.py --check
```
`--replace-download` は、本番 /download/ にスケッチ資料の選択肢が無い場合に付ける（本番版にすでにある場合は付けない）。

## 戻し方
- 最速：`/assets/ss-media-set-v1.css` に `.ssm{display:none}` の1行だけを書いて上書き（全ページから即座に消える）
- 完全：公開前バックアップの HTML を戻し、/assets/ss-media-set-v1.* と /videos/ を削除

## 計測
既存GA4がある場合のみ送る：動画再生 `video_play`（video_id）、資料ボタン `cta_click`（cta_type=doc_download, doc_id）。個人情報は送らない。資料請求の完了は FormSubmit のメール受信で数え、クリックを請求完了と数えない。

## 検査（2026-09-28 cloud・テスト用ミラー）
390px／1280px：横はみ出し0、JSエラー0、/download/?doc=sketch-triple-guard でスケッチ資料に自動チェック、再実行で二重に入らない（置き換え）。サムネ画像は cloud から YouTube に届かないため未表示（本番では表示される）。**本番ミラーでの実行・本番公開は未実施。**

## コラム（/column/）2026-09-28 更新
- 正本：`column/articles.json`（Notion 📝 note記事DB から取得）。`python3 column/build_column.py` で一覧と記事ページを再生成
- 掲載18本：note公開済み6本（noteへリンク）＋サイト内記事12本（/column/<slug>/、寺嵜承認 2026-09-28「OK」「保存OK」）
- サイト内記事の本文は Notion の「note本文開始〜終了」をそのまま転記（改稿なし）。各記事に 住宅/法人LINE・関連ページ・資料DLのCTA、Article構造化データ、関連記事3本
- 公開後は Notion note記事DB の「自社ブログURL」に各URLを記入すること
- 検査（cloud・テスト用ミラー）：13ページ×390/1280px 横はみ出し0・JSエラー0・/column/ 内リンク切れ0

- **/column.html（本番メニューの「コラム」）は新 /column/ への転送ページに置き換える**（2026-09-28 寺嵜指摘「コラム更新されてなくない？」）。旧「寺嵜が動画で答える」の動画は /videos/ と各LPの動画枠で見られる。本番ヘッダーの「コラム」リンク先を /column/ に直せる場合はそちらが望ましい
