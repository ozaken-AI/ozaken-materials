#!/usr/bin/env python3
"""/api/send の返事を人が読める形にして、終了コードで続きの有無を伝える。

    0  … 送り終えた（またはテスト送信が成功した）
    10 … まだ残っている。send.sh が叩き直す
    それ以外 … 中断すべき失敗
"""
import json
import sys

try:
    r = json.load(sys.stdin)
except Exception:
    print("  返事を読めませんでした（URL・トークン・D1の設定を確認してください）")
    sys.exit(3)

if not r.get("ok"):
    print("  失敗:", r.get("error"))
    sys.exit(4)

if r.get("test"):
    result = r.get("result", {})
    print("  テスト送信:", result.get("status"), result.get("error") or "")
    sys.exit(0 if result.get("status") == "sent" else 4)

print(f'  送信 {r["sent"]}件 / 失敗 {r["failed"]}件 / 残り {r["remaining"]}件')
for e in r.get("errors") or []:
    print("   -", e)

# 上限まで試しても送れなかった相手。黙って落とすと気づけないので、必ず名前を出す。
gave_up = r.get("gave_up") or []
if gave_up:
    print(f'  ▲ {len(gave_up)}件は{r.get("max_attempts", 3)}回試しても送れませんでした:')
    for g in gave_up[:20]:
        print("   -", g.get("email"), "/", (g.get("error") or "")[:120])
    if len(gave_up) > 20:
        print(f"   … ほか {len(gave_up) - 20}件")

sys.exit(0 if r.get("done") else 10)
