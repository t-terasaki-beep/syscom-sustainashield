# お名前.com 本番公開（単一経路・安全設計）

本番（お名前.com / nginx）への公開を **1本の手順**にまとめたものです。
公開処理は `deploy/publish.sh` に集約し、**PC（手元）でも GitHub Actions でも同じスクリプト**で動きます。

> 事実整理：本番ドメインは お名前.com 配信で **GitHub Pages ではありません**（Actions履歴の
> "pages build and deployment" は本番の配信経路ではない）。自己ホスト runner も存在しません。
> よって公開は「FTPで対象ファイルを上げる」= この1経路に統一します。

## このスクリプトが必ず守ること
1. **変更ファイルだけ**を対象（`deploy/changesets/<name>.txt` に列挙した分のみ）
2. **公開先未設定なら停止**（`FTP_*` 未設定・`FTP_REMOTE_ROOT` の末尾スラッシュ無しは即終了。`/` へフォールバックしない）
3. **本番削除は禁止**（逐次 `PUT` のみ。`DELETE` や mirror 同期は一切しない＝既存ファイルは消えない）
4. **公開前**＝差分表示・現行のバックアップ取得・**承認**、**公開後**＝本番URLを取り直して内容一致を検証

## A. PC（手元）で実行する ← 推奨（FTP資格情報を手元に留められる）
```bash
# 1) 手元に本リポジトリ（または配布された bundle）を用意
# 2) お名前.comのFTP設定を環境変数で渡す（値は保存されません）
export FTP_HOST="ftpXXX.onamae.ne.jp"
export FTP_USER="（FTPユーザー）"
export FTP_PASS="（FTPパスワード）"
export FTP_REMOTE_ROOT="/"          # 公開ドキュメントルート。末尾スラッシュ必須
# 3) まずプレビュー（差分とバックアップだけ。アップロードしない）
bash deploy/publish.sh deploy/changesets/chiba-blackout.txt
# 4) 差分に問題なければ本番公開（--yes で承認）
bash deploy/publish.sh deploy/changesets/chiba-blackout.txt --yes
```
- `FTP_REMOTE_ROOT` は「既存の成功した公開設定」から確定してください（ファイルマネージャーで
  `residential/` などが直下に見えるなら `/`、公開領域が `public_html` 配下なら `/public_html/`）。
- 実行後、`deploy/_runs/<日時>/backup/` に**元ファイルのバックアップ**が残ります（ロールバック可）。

## B. GitHub Actions で実行する（任意）
1. Settings → Secrets and variables → Actions に登録
   - Secrets: `FTP_HOST` `FTP_USER` `FTP_PASS` `FTP_REMOTE_ROOT`
   - 任意 Variables: `FTP_PROTOCOL`(既定 `ftps`) / `PUBLIC_BASE`
2. Settings → Environments → **`production`** に **Required reviewers** を設定（人の承認ゲート）
3. Actions →「Publish to Onamae」→ Run workflow
   - `changeset` を選択、`confirm` は空でプレビュー / `PUBLISH` で本番公開
   - 対象ファイルは **main に載っている必要**があります（例：chiba-blackout は PR #11 マージ後）

## changeset（対象ファイルの定義）
`deploy/changesets/*.txt` に「ローカル相対パス  リモート相対パス」を1行ずつ。
リモート相対は `FTP_REMOTE_ROOT` 基準（=公開ドキュメントルート基準）。
- `chiba-blackout.txt` … 千葉停電LPの**今回の2ファイル**（index.html / assets/story-plus.css）
- `residential-thermal.txt` … 戸建て冷暖塗装LPの web 2ファイル

## 阻害要因（＝本人が一度だけ行う操作）
このスクリプトは**公開先（FTP）が確定するまで動きません**（安全のため）。必要なのは次の一度きり：
- お名前.comの **FTPホスト / ユーザー / パスワード / 公開ドキュメントルート** を用意し、
  - PC実行なら 上記 env に設定、
  - Actions実行なら Secrets に登録。
- FTP が無効な契約の場合は、コントロールパネルで FTP を有効化（または SFTP 情報を用意）。
値は私（Claude）に共有不要です。設定後は上記の1コマンド（またはRun workflow）で公開できます。

## コラム公開（column-20260930）
- 対象：`deploy/changesets/column-20260930.txt`（25ファイル。assets → column/ → videos/ → column.html の順）
- ローカル側は PR #10 でマージ済みの `tools/publish/lp-media-set-v1/` を参照する（別途ビルド不要）
- `/column.html` は旧ページを「/column/ への転送ページ」で上書きする。戻すときは `deploy/_runs/<日時>/backup/column.html` を再アップロード
- 公開後：`https://syscom-sustaina-shield.com/column/` `/column.html` `/videos/` の表示と、記事内リンク先（/business/ /residential/ /download/ /hojokin/）の到達を確認
