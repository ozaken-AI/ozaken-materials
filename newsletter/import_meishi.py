#!/usr/bin/env python3
"""名刺管理サービス（Sansan / Eight）の書き出しCSVを、D1に入れるSQLに変える。

    python3 newsletter/import_meishi.py meishi.csv \
        --source-note "2026年上期 名刺交換" > newsletter/import.sql
    wrangler d1 execute ozaken-newsletter --remote --file=newsletter/import.sql

**すでに配信停止した人を復活させない。** ON CONFLICT では status に触らないので、
同じCSVを何度流し込んでも、止めた人は止まったまま。名前や会社名だけが新しくなる。

文字コードは cp932（Sansanの既定）と UTF-8 の両方を、順に試す。
"""

import argparse
import csv
import io
import re
import sys
from datetime import date, datetime

# 列の見出しは、サービスと書き出し設定でまちまち。左に書いたものから順に探す。
COLUMNS = {
    "email":   ["メールアドレス", "E-mail", "Email", "mail", "メール", "電子メール"],
    "last":    ["姓", "Last name", "苗字"],
    "first":   ["名", "First name", "下の名前"],
    "name":    ["氏名", "名前", "フルネーム", "Name", "担当者名"],
    "company": ["会社名", "企業名", "Company", "組織名", "勤務先"],
    "date":    ["名刺交換日", "交換日", "登録日", "取得日", "作成日"],
}

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s.]+\.[^@\s]+$")


def read_rows(path):
    raw = open(path, "rb").read()
    for encoding in ("utf-8-sig", "cp932", "utf-8"):
        try:
            text = raw.decode(encoding)
        except UnicodeDecodeError:
            continue
        rows = list(csv.DictReader(io.StringIO(text)))
        if rows and any(k for k in (rows[0].keys() or []) if k):
            return rows, encoding
    sys.exit("CSVを読めませんでした（文字コードを確認してください）。")


def find_column(fieldnames, candidates):
    cleaned = {(f or "").strip(): f for f in fieldnames}
    for want in candidates:
        for got, original in cleaned.items():
            if got == want:
                return original
    # 完全一致で見つからなければ、含まれているかで探す
    for want in candidates:
        for got, original in cleaned.items():
            if want and want in got:
                return original
    return None


def norm_email(value):
    return (value or "").replace("　", " ").strip().lower()


def norm_date(value, fallback):
    """名刺交換日を ISO8601 にそろえる。読めなければ取り込み日を使う。"""
    v = (value or "").strip()
    if not v:
        return fallback
    v = v.replace("年", "-").replace("月", "-").replace("日", "").strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M", "%Y-%m", "%Y/%m"):
        try:
            return datetime.strptime(v, fmt).date().isoformat() + "T00:00:00.000Z"
        except ValueError:
            continue
    return fallback


def sql_str(value):
    if value is None or value == "":
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"


def main():
    p = argparse.ArgumentParser(description="名刺CSVをD1投入用SQLに変換する")
    p.add_argument("csv_path")
    p.add_argument("--source-note", default=None,
                   help="取得の場をひとことで（例: 2026年上期 名刺交換）。記録として名簿に残る")
    p.add_argument("--source", default="meishi", help="取得経路。既定は meishi")
    p.add_argument("--status", default="active", choices=["active", "pending"],
                   help="active＝すぐ配信対象。pending＝確認メールを踏むまで送らない")
    p.add_argument("--email-column", default=None, help="メールアドレスの列名を明示する")
    p.add_argument("--exclude", default=None,
                   help="除外したいアドレスを1行1件で並べたファイル（競合他社など）")
    p.add_argument("-o", "--out", default=None, help="出力先。省略すると標準出力")
    args = p.parse_args()

    rows, encoding = read_rows(args.csv_path)
    fields = rows[0].keys()
    col = {k: find_column(fields, v) for k, v in COLUMNS.items()}
    if args.email_column:
        col["email"] = args.email_column
    if not col["email"]:
        sys.exit(f"メールアドレスの列が見つかりません。見出し: {list(fields)}")

    excluded = set()
    if args.exclude:
        with open(args.exclude, encoding="utf-8") as f:
            excluded = {norm_email(line) for line in f if line.strip()}

    today = date.today().isoformat() + "T00:00:00.000Z"
    seen, out, skipped_bad, skipped_dup, skipped_ex = {}, [], 0, 0, 0

    for row in rows:
        email = norm_email(row.get(col["email"]))
        if not EMAIL_RE.match(email):
            skipped_bad += 1
            continue
        if email in excluded:
            skipped_ex += 1
            continue
        if email in seen:
            skipped_dup += 1
            continue

        if col["name"] and (row.get(col["name"]) or "").strip():
            name = (row.get(col["name"]) or "").strip()
        else:
            parts = [(row.get(col[k]) or "").strip() for k in ("last", "first") if col.get(k)]
            name = " ".join(x for x in parts if x)

        seen[email] = {
            "name": name or None,
            "company": (row.get(col["company"]) or "").strip() if col["company"] else None,
            "consent_at": norm_date(row.get(col["date"]) if col["date"] else None, today),
        }

    for email, v in seen.items():
        out.append(
            "INSERT INTO subscribers "
            "(email, name, company, status, source, source_note, consent_at, created_at, updated_at) VALUES "
            f"({sql_str(email)}, {sql_str(v['name'])}, {sql_str(v['company'])}, "
            f"{sql_str(args.status)}, {sql_str(args.source)}, {sql_str(args.source_note)}, "
            f"{sql_str(v['consent_at'])}, {sql_str(today)}, {sql_str(today)}) "
            "ON CONFLICT(email) DO UPDATE SET "
            "name = COALESCE(excluded.name, subscribers.name), "
            "company = COALESCE(excluded.company, subscribers.company), "
            "updated_at = excluded.updated_at;"
        )
        # 同意（＝名刺で連絡先をもらった）記録。法令上、これが根拠になる。
        out.append(
            "INSERT INTO events (email, kind, detail, at) VALUES "
            f"({sql_str(email)}, 'import', "
            f"{sql_str((args.source_note or args.source) + ' / consent_at=' + v['consent_at'])}, "
            f"{sql_str(today)});"
        )

    header = [
        "-- newsletter/import_meishi.py が生成。手で書き足さない。",
        f"-- 元ファイル: {args.csv_path}（{encoding} として読めた）",
        f"-- 取り込み: {len(seen)}件 / 除外: 形式不正 {skipped_bad}, 重複 {skipped_dup}, 除外リスト {skipped_ex}",
        f"-- 列の対応: {', '.join(f'{k}→{v}' for k, v in col.items() if v)}",
        "",
    ]
    text = "\n".join(header + out) + "\n"

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)

    print(f"取り込み {len(seen)}件 / 形式不正 {skipped_bad} / 重複 {skipped_dup} / 除外 {skipped_ex}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
