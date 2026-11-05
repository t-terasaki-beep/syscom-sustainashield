#!/usr/bin/env bash
# =============================================================================
# お名前.com 安全公開スクリプト（単一経路 / PC・GitHub Actions 共通）
#
# 満たす要件（COO指示）:
#  1. 変更したファイルだけを対象  … changeset で明示（このスクリプトは列挙分のみ触る）
#  2. 公開先未設定なら停止        … FTP_* が未設定なら即終了（"/" フォールバック禁止）
#  3. 本番削除は禁止              … 逐次 PUT のみ。DELETE / mirror --delete を一切使わない
#  4. 公開前=差分・バックアップ・承認 / 公開後=本番再取得検証 を必須
#
# 使い方:
#   FTP_HOST=... FTP_USER=... FTP_PASS=... FTP_REMOTE_ROOT=/ \
#     bash deploy/publish.sh deploy/changesets/chiba-blackout.txt [--yes]
#   - --yes（または CONFIRM=PUBLISH）が無い場合は「差分表示までで停止」＝プレビュー
#   - LOCAL_ROOT を指定するとアップロード元ルートを変更可（既定=カレント）
# =============================================================================
set -eu

# ---- 公開先（未設定なら停止。フォールバックしない）--------------------------
: "${FTP_HOST:?停止: FTP_HOST 未設定（公開先未設定では実行しません）}"
: "${FTP_USER:?停止: FTP_USER 未設定}"
: "${FTP_PASS:?停止: FTP_PASS 未設定}"
: "${FTP_REMOTE_ROOT:?停止: FTP_REMOTE_ROOT 未設定（例 / または /public_html/。末尾スラッシュ必須。フォールバックしません）}"
FTP_PROTOCOL="${FTP_PROTOCOL:-ftps}"        # ftps(既定,明示的TLS) / ftp(非推奨)
PUBLIC_BASE="${PUBLIC_BASE:-https://syscom-sustaina-shield.com}"
LOCAL_ROOT="${LOCAL_ROOT:-$(pwd)}"

case "$FTP_REMOTE_ROOT" in
  */) : ;;
  *) echo "停止: FTP_REMOTE_ROOT は末尾スラッシュが必要（例 / ）"; exit 2 ;;
esac

# Never let FTP_REMOTE_ROOT normalize path separators, dot segments or
# encoded aliases into a production-only URL after the rp-only guard runs.
# A safe FTP destination root is an absolute, plain path ending in '/'.
case "$FTP_REMOTE_ROOT" in
  /*) : ;;
  *) echo "停止: FTP_REMOTE_ROOT は / で始まる正規パスが必要"; exit 3 ;;
esac
case "$FTP_REMOTE_ROOT" in
  *'%'*|*'\\'*|*'?'*|*'#'*|*//*|*/../*|*/./*|*
CONFIRM_FLAG="${2:-}"
[ -f "$CHANGESET" ] || { echo "停止: changeset が見つからない: $CHANGESET"; exit 2; }

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
WORK="deploy/_runs/$STAMP"
BACKUP="$WORK/backup"
mkdir -p "$BACKUP"

CURL="curl --fail --show-error --silent --connect-timeout 20 --max-time 180"
[ "$FTP_PROTOCOL" = "ftps" ] && CURL="$CURL --ftp-ssl"

# ---- changeset 読み込み（"local  remote"、2列目省略時は1列目を流用）--------
LOCS=""; REMS=""
while IFS= read -r line || [ -n "$line" ]; do
  # Windows CRLF or embedded CR can turn a protected target into a different
  # FTP remote filename when awk parses a trailing carriage return.
  # Reject ambiguous changesets before checking protected production paths.
  case "$line" in
    *$'\r'*) echo "停止: changeset に CR 制御文字があります。LF 改行に変換してください"; exit 3 ;;
  esac
  case "$line" in ''|\#*) continue ;; esac
  lp="$(printf '%s\n' "$line" | awk '{print $1}')"
  rp="$(printf '%s\n' "$line" | awk '{if ($2!="") print $2; else print $1}')"
  # Production-only or live-divergent files and their entire subtrees
  # are NOT deployable from GitHub (including newly added assets).
  # P0 column repair must use the separately authorized, locked live-file
  # patch workflow, never a repository-generated replacement.
  # Reject URL-encoded separators/aliases, Windows separators, URL suffixes,
  # and terminal dot segments BEFORE any network activity.
  # This is intentionally conservative: release paths must be plain relative paths.
  # FTP_REMOTE_ROOT may be / or /public_html/; reject protected target paths
  # even when a changeset embeds public_html/, www/, or another parent prefix.
  case "$rp" in
    /*|./*|../*|*/../*|*/./*|*//*|*/..|*/.|.|..|*'%'*|*'\'*|*'?'*|*'#'*)
      echo "停止: 非正規のリモート相対パス: $rp"; exit 3 ;;
    column/chiba-suigai-hinanjo-dengen|column/chiba-suigai-hinanjo-dengen/*|*/column/chiba-suigai-hinanjo-dengen|*/column/chiba-suigai-hinanjo-dengen/*|photo-diagnosis|photo-diagnosis/*|*/photo-diagnosis|*/photo-diagnosis/*|shindan.html|*/shindan.html)
      echo "停止: 本番専用・差異ありの保護URLはGitHubから上書き禁止: $rp"; exit 3 ;;
  esac
  # Guard the EFFECTIVE FTP destination, not only the manifest's rp.
  # FTP_REMOTE_ROOT may itself point at a protected article directory, making
  # an apparently safe 'index.html' write overwrite the production-only page.
  effective_rp="${FTP_REMOTE_ROOT#/}$rp"
  case "$effective_rp" in
    column/chiba-suigai-hinanjo-dengen|column/chiba-suigai-hinanjo-dengen/*|*/column/chiba-suigai-hinanjo-dengen|*/column/chiba-suigai-hinanjo-dengen/*|photo-diagnosis|photo-diagnosis/*|*/photo-diagnosis|*/photo-diagnosis/*|shindan.html|*/shindan.html)
      echo "停止: FTP_REMOTE_ROOT を含む実効公開先が本番保護URLです。GitHubから上書き禁止: $effective_rp"; exit 3 ;;
  esac
  [ -f "$LOCAL_ROOT/$lp" ] || { echo "停止: ローカルに無い: $LOCAL_ROOT/$lp"; exit 2; }
  LOCS="$LOCS$lp"$'\n'; REMS="$REMS$rp"$'\n'
done < "$CHANGESET"
[ -n "$LOCS" ] || { echo "停止: changeset が空"; exit 2; }

echo "== 対象（変更ファイルのみ）$STAMP =="
paste <(printf '%s' "$LOCS") <(printf '%s' "$REMS") | while IFS="$(printf '\t')" read -r lp rp; do
  [ -n "$lp" ] && echo "  $lp  ->  ${FTP_REMOTE_ROOT}$rp"
done

# ---- バックアップ（現行リモート取得）＋差分 --------------------------------
echo "== バックアップ＆差分（remote → new）=="
paste <(printf '%s' "$LOCS") <(printf '%s' "$REMS") | while IFS="$(printf '\t')" read -r lp rp; do
  [ -n "$lp" ] || continue
  url="${FTP_PROTOCOL}://${FTP_HOST}${FTP_REMOTE_ROOT}${rp}"
  mkdir -p "$BACKUP/$(dirname "$rp")"
  if $CURL --user "$FTP_USER:$FTP_PASS" -o "$BACKUP/$rp" "$url" 2>/dev/null; then
    echo "-- $rp"
    diff -u "$BACKUP/$rp" "$LOCAL_ROOT/$lp" | sed -n '1,60p' || true
  else
    echo "-- $rp （リモートに現行なし＝新規追加）"
  fi
done
echo "  バックアップ保存先: $BACKUP"

# ---- 承認確認 --------------------------------------------------------------
if [ "$CONFIRM_FLAG" != "--yes" ] && [ "${CONFIRM:-}" != "PUBLISH" ]; then
  echo
  echo "【承認待ち】上記の差分で本番公開します。実行するには --yes または CONFIRM=PUBLISH を付けて再実行してください。"
  echo "（ここまでは無害なプレビュー：バックアップと差分のみ。アップロードは行っていません）"
  exit 10
fi

# ---- アップロード（逐次 PUT のみ・削除しない）------------------------------
echo "== アップロード（PUTのみ・本番削除はしません）=="
paste <(printf '%s' "$LOCS") <(printf '%s' "$REMS") | while IFS="$(printf '\t')" read -r lp rp; do
  [ -n "$lp" ] || continue
  url="${FTP_PROTOCOL}://${FTP_HOST}${FTP_REMOTE_ROOT}${rp}"
  $CURL --ftp-create-dirs --user "$FTP_USER:$FTP_PASS" -T "$LOCAL_ROOT/$lp" "$url"
  echo "  uploaded: $rp"
done

# ---- 公開後：本番再取得検証（HTTPSで実物を取り直し照合）--------------------
echo "== 本番再取得検証 =="
FAIL=0
paste <(printf '%s' "$LOCS") <(printf '%s' "$REMS") | while IFS="$(printf '\t')" read -r lp rp; do
  [ -n "$lp" ] || continue
  purl="${PUBLIC_BASE}/${rp}"
  out="$WORK/verify_$(printf '%s' "$rp" | tr '/' '_')"
  code="$(curl -s -o "$out" -w '%{http_code}' "$purl" || echo 000)"
  if [ "$code" = "200" ] && cmp -s "$out" "$LOCAL_ROOT/$lp"; then
    echo "  OK  200 & 内容一致: $purl"
  else
    echo "  NG  code=$code / 内容不一致: $purl（CDN/キャッシュの可能性。時間をおいて再確認 or backup でロールバック）"
    echo "$rp" >> "$WORK/verify_failures.txt"
  fi
done
if [ -f "$WORK/verify_failures.txt" ]; then
  echo "❌ 検証失敗あり。ロールバック用バックアップ: $BACKUP"
  exit 20
fi
echo "✅ 公開＆本番再取得検証 完了（$STAMP）  バックアップ: $BACKUP"
\\r'*|*
CONFIRM_FLAG="${2:-}"
[ -f "$CHANGESET" ] || { echo "停止: changeset が見つからない: $CHANGESET"; exit 2; }

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
WORK="deploy/_runs/$STAMP"
BACKUP="$WORK/backup"
mkdir -p "$BACKUP"

CURL="curl --fail --show-error --silent --connect-timeout 20 --max-time 180"
[ "$FTP_PROTOCOL" = "ftps" ] && CURL="$CURL --ftp-ssl"

# ---- changeset 読み込み（"local  remote"、2列目省略時は1列目を流用）--------
LOCS=""; REMS=""
while IFS= read -r line || [ -n "$line" ]; do
  # Windows CRLF or embedded CR can turn a protected target into a different
  # FTP remote filename when awk parses a trailing carriage return.
  # Reject ambiguous changesets before checking protected production paths.
  case "$line" in
    *$'\r'*) echo "停止: changeset に CR 制御文字があります。LF 改行に変換してください"; exit 3 ;;
  esac
  case "$line" in ''|\#*) continue ;; esac
  lp="$(printf '%s\n' "$line" | awk '{print $1}')"
  rp="$(printf '%s\n' "$line" | awk '{if ($2!="") print $2; else print $1}')"
  # Production-only or live-divergent files and their entire subtrees
  # are NOT deployable from GitHub (including newly added assets).
  # P0 column repair must use the separately authorized, locked live-file
  # patch workflow, never a repository-generated replacement.
  # Reject URL-encoded separators/aliases, Windows separators, URL suffixes,
  # and terminal dot segments BEFORE any network activity.
  # This is intentionally conservative: release paths must be plain relative paths.
  # FTP_REMOTE_ROOT may be / or /public_html/; reject protected target paths
  # even when a changeset embeds public_html/, www/, or another parent prefix.
  case "$rp" in
    /*|./*|../*|*/../*|*/./*|*//*|*/..|*/.|.|..|*'%'*|*'\'*|*'?'*|*'#'*)
      echo "停止: 非正規のリモート相対パス: $rp"; exit 3 ;;
    column/chiba-suigai-hinanjo-dengen|column/chiba-suigai-hinanjo-dengen/*|*/column/chiba-suigai-hinanjo-dengen|*/column/chiba-suigai-hinanjo-dengen/*|photo-diagnosis|photo-diagnosis/*|*/photo-diagnosis|*/photo-diagnosis/*|shindan.html|*/shindan.html)
      echo "停止: 本番専用・差異ありの保護URLはGitHubから上書き禁止: $rp"; exit 3 ;;
  esac
  # Guard the EFFECTIVE FTP destination, not only the manifest's rp.
  # FTP_REMOTE_ROOT may itself point at a protected article directory, making
  # an apparently safe 'index.html' write overwrite the production-only page.
  effective_rp="${FTP_REMOTE_ROOT#/}$rp"
  case "$effective_rp" in
    column/chiba-suigai-hinanjo-dengen|column/chiba-suigai-hinanjo-dengen/*|*/column/chiba-suigai-hinanjo-dengen|*/column/chiba-suigai-hinanjo-dengen/*|photo-diagnosis|photo-diagnosis/*|*/photo-diagnosis|*/photo-diagnosis/*|shindan.html|*/shindan.html)
      echo "停止: FTP_REMOTE_ROOT を含む実効公開先が本番保護URLです。GitHubから上書き禁止: $effective_rp"; exit 3 ;;
  esac
  [ -f "$LOCAL_ROOT/$lp" ] || { echo "停止: ローカルに無い: $LOCAL_ROOT/$lp"; exit 2; }
  LOCS="$LOCS$lp"$'\n'; REMS="$REMS$rp"$'\n'
done < "$CHANGESET"
[ -n "$LOCS" ] || { echo "停止: changeset が空"; exit 2; }

echo "== 対象（変更ファイルのみ）$STAMP =="
paste <(printf '%s' "$LOCS") <(printf '%s' "$REMS") | while IFS="$(printf '\t')" read -r lp rp; do
  [ -n "$lp" ] && echo "  $lp  ->  ${FTP_REMOTE_ROOT}$rp"
done

# ---- バックアップ（現行リモート取得）＋差分 --------------------------------
echo "== バックアップ＆差分（remote → new）=="
paste <(printf '%s' "$LOCS") <(printf '%s' "$REMS") | while IFS="$(printf '\t')" read -r lp rp; do
  [ -n "$lp" ] || continue
  url="${FTP_PROTOCOL}://${FTP_HOST}${FTP_REMOTE_ROOT}${rp}"
  mkdir -p "$BACKUP/$(dirname "$rp")"
  if $CURL --user "$FTP_USER:$FTP_PASS" -o "$BACKUP/$rp" "$url" 2>/dev/null; then
    echo "-- $rp"
    diff -u "$BACKUP/$rp" "$LOCAL_ROOT/$lp" | sed -n '1,60p' || true
  else
    echo "-- $rp （リモートに現行なし＝新規追加）"
  fi
done
echo "  バックアップ保存先: $BACKUP"

# ---- 承認確認 --------------------------------------------------------------
if [ "$CONFIRM_FLAG" != "--yes" ] && [ "${CONFIRM:-}" != "PUBLISH" ]; then
  echo
  echo "【承認待ち】上記の差分で本番公開します。実行するには --yes または CONFIRM=PUBLISH を付けて再実行してください。"
  echo "（ここまでは無害なプレビュー：バックアップと差分のみ。アップロードは行っていません）"
  exit 10
fi

# ---- アップロード（逐次 PUT のみ・削除しない）------------------------------
echo "== アップロード（PUTのみ・本番削除はしません）=="
paste <(printf '%s' "$LOCS") <(printf '%s' "$REMS") | while IFS="$(printf '\t')" read -r lp rp; do
  [ -n "$lp" ] || continue
  url="${FTP_PROTOCOL}://${FTP_HOST}${FTP_REMOTE_ROOT}${rp}"
  $CURL --ftp-create-dirs --user "$FTP_USER:$FTP_PASS" -T "$LOCAL_ROOT/$lp" "$url"
  echo "  uploaded: $rp"
done

# ---- 公開後：本番再取得検証（HTTPSで実物を取り直し照合）--------------------
echo "== 本番再取得検証 =="
FAIL=0
paste <(printf '%s' "$LOCS") <(printf '%s' "$REMS") | while IFS="$(printf '\t')" read -r lp rp; do
  [ -n "$lp" ] || continue
  purl="${PUBLIC_BASE}/${rp}"
  out="$WORK/verify_$(printf '%s' "$rp" | tr '/' '_')"
  code="$(curl -s -o "$out" -w '%{http_code}' "$purl" || echo 000)"
  if [ "$code" = "200" ] && cmp -s "$out" "$LOCAL_ROOT/$lp"; then
    echo "  OK  200 & 内容一致: $purl"
  else
    echo "  NG  code=$code / 内容不一致: $purl（CDN/キャッシュの可能性。時間をおいて再確認 or backup でロールバック）"
    echo "$rp" >> "$WORK/verify_failures.txt"
  fi
done
if [ -f "$WORK/verify_failures.txt" ]; then
  echo "❌ 検証失敗あり。ロールバック用バックアップ: $BACKUP"
  exit 20
fi
echo "✅ 公開＆本番再取得検証 完了（$STAMP）  バックアップ: $BACKUP"
\\n'*)
    echo "停止: 非正規の FTP_REMOTE_ROOT。公開先を見直してください"; exit 3 ;;
esac

CHANGESET="${1:?使い方: publish.sh <changesetファイル> [--yes]}"
CONFIRM_FLAG="${2:-}"
[ -f "$CHANGESET" ] || { echo "停止: changeset が見つからない: $CHANGESET"; exit 2; }

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
WORK="deploy/_runs/$STAMP"
BACKUP="$WORK/backup"
mkdir -p "$BACKUP"

CURL="curl --fail --show-error --silent --connect-timeout 20 --max-time 180"
[ "$FTP_PROTOCOL" = "ftps" ] && CURL="$CURL --ftp-ssl"

# ---- changeset 読み込み（"local  remote"、2列目省略時は1列目を流用）--------
LOCS=""; REMS=""
while IFS= read -r line || [ -n "$line" ]; do
  # Windows CRLF or embedded CR can turn a protected target into a different
  # FTP remote filename when awk parses a trailing carriage return.
  # Reject ambiguous changesets before checking protected production paths.
  case "$line" in
    *$'\r'*) echo "停止: changeset に CR 制御文字があります。LF 改行に変換してください"; exit 3 ;;
  esac
  case "$line" in ''|\#*) continue ;; esac
  lp="$(printf '%s\n' "$line" | awk '{print $1}')"
  rp="$(printf '%s\n' "$line" | awk '{if ($2!="") print $2; else print $1}')"
  # Production-only or live-divergent files and their entire subtrees
  # are NOT deployable from GitHub (including newly added assets).
  # P0 column repair must use the separately authorized, locked live-file
  # patch workflow, never a repository-generated replacement.
  # Reject URL-encoded separators/aliases, Windows separators, URL suffixes,
  # and terminal dot segments BEFORE any network activity.
  # This is intentionally conservative: release paths must be plain relative paths.
  # FTP_REMOTE_ROOT may be / or /public_html/; reject protected target paths
  # even when a changeset embeds public_html/, www/, or another parent prefix.
  case "$rp" in
    /*|./*|../*|*/../*|*/./*|*//*|*/..|*/.|.|..|*'%'*|*'\'*|*'?'*|*'#'*)
      echo "停止: 非正規のリモート相対パス: $rp"; exit 3 ;;
    column/chiba-suigai-hinanjo-dengen|column/chiba-suigai-hinanjo-dengen/*|*/column/chiba-suigai-hinanjo-dengen|*/column/chiba-suigai-hinanjo-dengen/*|photo-diagnosis|photo-diagnosis/*|*/photo-diagnosis|*/photo-diagnosis/*|shindan.html|*/shindan.html)
      echo "停止: 本番専用・差異ありの保護URLはGitHubから上書き禁止: $rp"; exit 3 ;;
  esac
  # Guard the EFFECTIVE FTP destination, not only the manifest's rp.
  # FTP_REMOTE_ROOT may itself point at a protected article directory, making
  # an apparently safe 'index.html' write overwrite the production-only page.
  effective_rp="${FTP_REMOTE_ROOT#/}$rp"
  case "$effective_rp" in
    column/chiba-suigai-hinanjo-dengen|column/chiba-suigai-hinanjo-dengen/*|*/column/chiba-suigai-hinanjo-dengen|*/column/chiba-suigai-hinanjo-dengen/*|photo-diagnosis|photo-diagnosis/*|*/photo-diagnosis|*/photo-diagnosis/*|shindan.html|*/shindan.html)
      echo "停止: FTP_REMOTE_ROOT を含む実効公開先が本番保護URLです。GitHubから上書き禁止: $effective_rp"; exit 3 ;;
  esac
  [ -f "$LOCAL_ROOT/$lp" ] || { echo "停止: ローカルに無い: $LOCAL_ROOT/$lp"; exit 2; }
  LOCS="$LOCS$lp"$'\n'; REMS="$REMS$rp"$'\n'
done < "$CHANGESET"
[ -n "$LOCS" ] || { echo "停止: changeset が空"; exit 2; }

echo "== 対象（変更ファイルのみ）$STAMP =="
paste <(printf '%s' "$LOCS") <(printf '%s' "$REMS") | while IFS="$(printf '\t')" read -r lp rp; do
  [ -n "$lp" ] && echo "  $lp  ->  ${FTP_REMOTE_ROOT}$rp"
done

# ---- バックアップ（現行リモート取得）＋差分 --------------------------------
echo "== バックアップ＆差分（remote → new）=="
paste <(printf '%s' "$LOCS") <(printf '%s' "$REMS") | while IFS="$(printf '\t')" read -r lp rp; do
  [ -n "$lp" ] || continue
  url="${FTP_PROTOCOL}://${FTP_HOST}${FTP_REMOTE_ROOT}${rp}"
  mkdir -p "$BACKUP/$(dirname "$rp")"
  if $CURL --user "$FTP_USER:$FTP_PASS" -o "$BACKUP/$rp" "$url" 2>/dev/null; then
    echo "-- $rp"
    diff -u "$BACKUP/$rp" "$LOCAL_ROOT/$lp" | sed -n '1,60p' || true
  else
    echo "-- $rp （リモートに現行なし＝新規追加）"
  fi
done
echo "  バックアップ保存先: $BACKUP"

# ---- 承認確認 --------------------------------------------------------------
if [ "$CONFIRM_FLAG" != "--yes" ] && [ "${CONFIRM:-}" != "PUBLISH" ]; then
  echo
  echo "【承認待ち】上記の差分で本番公開します。実行するには --yes または CONFIRM=PUBLISH を付けて再実行してください。"
  echo "（ここまでは無害なプレビュー：バックアップと差分のみ。アップロードは行っていません）"
  exit 10
fi

# ---- アップロード（逐次 PUT のみ・削除しない）------------------------------
echo "== アップロード（PUTのみ・本番削除はしません）=="
paste <(printf '%s' "$LOCS") <(printf '%s' "$REMS") | while IFS="$(printf '\t')" read -r lp rp; do
  [ -n "$lp" ] || continue
  url="${FTP_PROTOCOL}://${FTP_HOST}${FTP_REMOTE_ROOT}${rp}"
  $CURL --ftp-create-dirs --user "$FTP_USER:$FTP_PASS" -T "$LOCAL_ROOT/$lp" "$url"
  echo "  uploaded: $rp"
done

# ---- 公開後：本番再取得検証（HTTPSで実物を取り直し照合）--------------------
echo "== 本番再取得検証 =="
FAIL=0
paste <(printf '%s' "$LOCS") <(printf '%s' "$REMS") | while IFS="$(printf '\t')" read -r lp rp; do
  [ -n "$lp" ] || continue
  purl="${PUBLIC_BASE}/${rp}"
  out="$WORK/verify_$(printf '%s' "$rp" | tr '/' '_')"
  code="$(curl -s -o "$out" -w '%{http_code}' "$purl" || echo 000)"
  if [ "$code" = "200" ] && cmp -s "$out" "$LOCAL_ROOT/$lp"; then
    echo "  OK  200 & 内容一致: $purl"
  else
    echo "  NG  code=$code / 内容不一致: $purl（CDN/キャッシュの可能性。時間をおいて再確認 or backup でロールバック）"
    echo "$rp" >> "$WORK/verify_failures.txt"
  fi
done
if [ -f "$WORK/verify_failures.txt" ]; then
  echo "❌ 検証失敗あり。ロールバック用バックアップ: $BACKUP"
  exit 20
fi
echo "✅ 公開＆本番再取得検証 完了（$STAMP）  バックアップ: $BACKUP"
