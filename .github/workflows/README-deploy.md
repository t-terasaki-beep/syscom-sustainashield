# お名前.com への自動デプロイ 設定手順

`deploy-onamae.yml` は、**リポジトリで管理している特定サブツリーだけ**を本番（お名前.com / FTP）へ反映します。
サイト全体は同期せず、**リモートの削除も行いません**（gitに無い本番ファイルは触りません）。

現在の対象サブツリー：
- `residential/chiba-blackout/` → 本番 `/residential/chiba-blackout/`
- `residential-thermal/`（`README.md`・`content/`・`templates/` は本番へ出さず除外）→ 本番 `/residential-thermal/`

## 1. FTPアカウントを用意
お名前.com のレンタルサーバー管理画面でFTPアカウント（ホスト名・ユーザー・パスワード）を確認/発行します。
可能なら **FTPS（明示的TLS）** を使えるアカウントにしてください（既定は `ftps`）。

## 2. GitHub にシークレット/変数を登録
リポジトリ **Settings → Secrets and variables → Actions**

**Secrets（必須）**
| 名前 | 値の例 |
| --- | --- |
| `FTP_SERVER` | `ftpXXX.onamae.ne.jp` |
| `FTP_USERNAME` | FTPユーザー名 |
| `FTP_PASSWORD` | FTPパスワード |

**Variables（任意）**
| 名前 | 既定 | 用途 |
| --- | --- | --- |
| `FTP_REMOTE_ROOT` | `/` | 本番ドキュメントルートのFTP上パス（末尾スラッシュ必須）。ファイルマネージャーで `residential/` 等が直下に見えるなら `/` のまま。公開領域が `public_html` 配下なら `/public_html/` 等 |
| `FTP_PROTOCOL` | `ftps` | `ftps` / `ftp` / `ftps-legacy` |
| `FTP_PORT` | `21` | 接続ポート |

> シークレットの値は私（Claude）に共有不要です。GitHubの画面で登録してください。

## 3. まず dry-run で安全確認
**Actions タブ → 「Deploy to Onamae」→ Run workflow**（`dry_run` は `true` のまま実行）。
- 実ファイルは転送されません。ログに「転送予定の差分」と接続結果が出ます。
- `server-dir` が正しい本番パスを指しているか（`FTP_REMOTE_ROOT` の要否）をここで確認します。

## 4. 本番反映
- 手動：Run workflow を `dry_run=false` で実行。
- 自動：対象サブツリーの変更が `main` に入る（PRマージ等）と、その配下だけを自動アップロード。

## 安全上の約束（設計）
- `dangerous-clean-slate: false` 固定＝**リモート削除なし**。
- `local-dir` は必ず特定サブフォルダ（`./` 全体にしない）。
- 初回転送はそのサブツリーの中身を本番へ上書きします（＝gitの内容で意図的に更新）。
  他ディレクトリ・サイト全体には影響しません。

## 対象を増やすとき
`deploy-onamae.yml` の `jobs.deploy.steps` にステップを1つ追加し、`local-dir` と `server-dir` を
新しいサブツリーに設定するだけです。`push.paths` にもそのパスを足すと自動反映の対象になります。
