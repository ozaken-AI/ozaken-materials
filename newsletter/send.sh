#!/usr/bin/env bash
# 号を1本、最後まで配る。
#
#   export NEWSLETTER_ADMIN_TOKEN=...            # /api/send を叩く鍵
#   ./newsletter/send.sh --test me@example.com newsletter/issues/2026-08-18.json
#   ./newsletter/send.sh newsletter/issues/2026-08-18.json
#
# /api/send は1回につき limit 件しか送らない（Workersの実行時間とResendのレート制限のため）。
# ここで「残り0件」になるまで叩き直す。途中で止めても、叩き直せば続きから再開する。

set -euo pipefail

ENDPOINT="${NEWSLETTER_ENDPOINT:-https://content.ozaken.ai/api/send}"
LIMIT="${NEWSLETTER_LIMIT:-500}"
TEST_TO=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --test)  TEST_TO="$2"; shift 2 ;;
    --limit) LIMIT="$2"; shift 2 ;;
    -*)      echo "知らない指定: $1" >&2; exit 2 ;;
    *)       ISSUE="$1"; shift ;;
  esac
done

: "${ISSUE:?号のJSONファイルを渡してください（例: newsletter/issues/2026-08-18.json）}"
: "${NEWSLETTER_ADMIN_TOKEN:?環境変数 NEWSLETTER_ADMIN_TOKEN が要ります}"
[[ -f "$ISSUE" ]] || { echo "ファイルがありません: $ISSUE" >&2; exit 1; }

# JSONの組み立てとほどきは python3 に任せる（jq が入っていない環境があるため）。
post() {
  local body="$1"
  curl -sS -X POST "$ENDPOINT" \
    -H "Authorization: Bearer ${NEWSLETTER_ADMIN_TOKEN}" \
    -H "Content-Type: application/json" \
    --data-binary "$body"
}

wrap() {
  ISSUE_PATH="$ISSUE" LIMIT="$LIMIT" TEST_TO="${1:-}" python3 - <<'PY'
import json, os, sys
issue = json.load(open(os.environ["ISSUE_PATH"], encoding="utf-8"))
payload = {"issue": issue, "limit": int(os.environ["LIMIT"])}
if os.environ.get("TEST_TO"):
    payload["test_to"] = os.environ["TEST_TO"]
sys.stdout.write(json.dumps(payload, ensure_ascii=False))
PY
}

show() {
  python3 "$(dirname "$0")/_report.py"
}

if [[ -n "$TEST_TO" ]]; then
  echo "テスト送信 → ${TEST_TO}"
  post "$(wrap "$TEST_TO")" | show
  exit 0
fi

echo "配信します: ${ISSUE}"
round=0
while true; do
  round=$((round + 1))
  echo "[$round 回目]"
  set +e
  post "$(wrap)" | show
  code=$?
  set -e
  case $code in
    0)  echo "配信を終えました。"; break ;;
    10) sleep 1 ;;                       # まだ残っている。少し置いて続ける
    *)  echo "中断しました。設定を直して同じコマンドを叩き直せば、続きから再開します。" >&2; exit $code ;;
  esac
done
