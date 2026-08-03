#!/usr/bin/env python3
"""
限定公開資料（パスワード暗号化されたHTML）の復号・再暗号化ツール。

このアーカイブのHTMLは、次の二段構えで暗号化されている。

    パスワード ──PBKDF2(SHA-256, 200k)──▶ ラップ鍵 ──AES-GCM──▶ コンテンツ鍵
    コンテンツ鍵 ──AES-GCM──▶ 本文HTML（CT）

再暗号化するときは **コンテンツ鍵をそのまま使い回す**。
こうすると W（ラップ済みコンテンツ鍵の配列）が変わらないので、
既存のパスワードが全部そのまま生き続ける。

使い方:
    # 復号して中身を取り出す
    python3 archive_crypto.py decrypt 07_リスク・法務/rogue-agents.html -o /tmp/plain.html

    # 編集した中身で詰め直す（元ファイルを上書き）
    python3 archive_crypto.py encrypt 07_リスク・法務/rogue-agents.html /tmp/plain.html

    # ラウンドトリップの自己テスト（パスワード不要）
    python3 archive_crypto.py selftest

パスワードは、この優先順で探す:
    1. --password で渡した値
    2. 環境変数 OZAKEN_ARCHIVE_PW
    3. 対話プロンプト（getpass）

⚠️ パスワードをリポジトリに書かないこと。環境変数で渡すこと。
"""

import argparse
import base64
import getpass
import json
import os
import re
import sys

try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except Exception as _e:  # pyo3 の PanicException は ImportError ではないので Exception で受ける
    sys.exit(
        f"cryptography を読み込めない: {_e}\n"
        "クリーンな環境では cffi が入っておらず失敗することがある。次で直る:\n"
        "    pip install cffi\n"
        "それでも直らなければ:\n"
        "    pip install --force-reinstall cryptography"
    )

RE_CT = re.compile(r'(var CT=")([A-Za-z0-9+/=]+)(")')
RE_IVC = re.compile(r'(IVC=")([A-Za-z0-9+/=]+)(")')
RE_W = re.compile(r'W=(\[.*?\]),ITER=(\d+)', re.S)


class ArchiveError(Exception):
    pass


def _b64d(s: str) -> bytes:
    return base64.b64decode(s)


def _b64e(b: bytes) -> str:
    return base64.b64encode(b).decode()


def parse(html: str):
    """暗号化HTMLから CT / IVC / W / ITER を取り出す。"""
    m_ct, m_ivc, m_w = RE_CT.search(html), RE_IVC.search(html), RE_W.search(html)
    if not (m_ct and m_ivc and m_w):
        raise ArchiveError(
            "暗号化された資料ではないか、形式が変わっている（CT / IVC / W が見つからない）"
        )
    return {
        "ct": m_ct.group(2),
        "ivc": m_ivc.group(2),
        "wrapped": json.loads(m_w.group(1)),
        "iters": int(m_w.group(2)),
    }


def unwrap_content_key(meta, password: str) -> bytes:
    """パスワードでコンテンツ鍵を取り出す。W を順に試す（複数パスワード対応のため）。"""
    for w in meta["wrapped"]:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=_b64d(w["s"]),
            iterations=meta["iters"],
        )
        try:
            wrap_key = kdf.derive(password.encode())
            return AESGCM(wrap_key).decrypt(_b64d(w["iv"]), _b64d(w["ct"]), None)
        except Exception:
            continue
    raise ArchiveError("パスワードが違う（どのラップ鍵でもコンテンツ鍵を開けなかった）")


def decrypt_html(html: str, password: str) -> str:
    meta = parse(html)
    ck = unwrap_content_key(meta, password)
    pt = AESGCM(ck).decrypt(_b64d(meta["ivc"]), _b64d(meta["ct"]), None)
    return pt.decode("utf-8")


def encrypt_html(html: str, plaintext: str, password: str) -> str:
    """外殻（ロック画面・W・ITER）はそのままに、CT と IVC だけ差し替えた HTML を返す。"""
    meta = parse(html)
    ck = unwrap_content_key(meta, password)  # 鍵は使い回す＝既存パスワードが生き続ける
    iv = os.urandom(12)
    ct = AESGCM(ck).encrypt(iv, plaintext.encode("utf-8"), None)

    out = RE_CT.sub(lambda m: m.group(1) + _b64e(ct) + m.group(3), html, count=1)
    out = RE_IVC.sub(lambda m: m.group(1) + _b64e(iv) + m.group(3), out, count=1)

    # 詰め直した結果が本当に元に戻せるか、ここで必ず確認する
    if decrypt_html(out, password) != plaintext:
        raise ArchiveError("再暗号化の検証に失敗した。ファイルは書き換えていない")
    return out


def get_password(arg: str | None) -> str:
    pw = arg or os.environ.get("OZAKEN_ARCHIVE_PW")
    if not pw:
        if not sys.stdin.isatty():
            raise ArchiveError(
                "パスワードが無い。環境変数 OZAKEN_ARCHIVE_PW を設定するか --password で渡すこと"
            )
        pw = getpass.getpass("アーカイブのパスワード: ")
    return pw


def build_test_file(password: str, body: str) -> str:
    """自己テスト用に、本物と同じ構造の暗号化HTMLを組み立てる。"""
    ck = os.urandom(32)
    salt, wiv = os.urandom(16), os.urandom(12)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=1000)
    wrapped = AESGCM(kdf.derive(password.encode())).encrypt(wiv, ck, None)
    iv = os.urandom(12)
    ct = AESGCM(ck).encrypt(iv, body.encode(), None)
    w = json.dumps([{"s": _b64e(salt), "iv": _b64e(wiv), "ct": _b64e(wrapped)}])
    return (
        f'<body><div class="lock">ロック画面</div>\n<script>\n'
        f'var CT="{_b64e(ct)}",IVC="{_b64e(iv)}",W={w},ITER=1000,'
        f'KEY="ozaken_archive_pw";\n</script></body>'
    )


def selftest() -> int:
    pw, body = "test-password-123", "<h1>本文</h1><p>日本語も通ること。</p>"
    src = build_test_file(pw, body)

    assert decrypt_html(src, pw) == body, "復号が一致しない"
    print("  ✓ 復号")

    edited = body + "<p>追記した段落。</p>"
    out = encrypt_html(src, edited, pw)
    assert decrypt_html(out, pw) == edited, "再暗号化後の復号が一致しない"
    print("  ✓ 再暗号化 → 復号")

    meta_a, meta_b = parse(src), parse(out)
    assert meta_a["wrapped"] == meta_b["wrapped"], "W が変わった（既存パスワードが死ぬ）"
    assert meta_a["iters"] == meta_b["iters"], "ITER が変わった"
    assert meta_a["ivc"] != meta_b["ivc"], "IV が使い回されている（AES-GCMでは致命的）"
    print("  ✓ W・ITER は不変 / IV は毎回新しい")

    assert '<div class="lock">ロック画面</div>' in out, "ロック画面の外殻が壊れた"
    print("  ✓ 外殻を保持")

    try:
        decrypt_html(src, "wrong-password")
    except ArchiveError:
        print("  ✓ 誤ったパスワードは弾く")
    else:
        raise AssertionError("誤ったパスワードが通ってしまった")

    print("\nselftest OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("decrypt", help="暗号化HTMLから本文を取り出す")
    d.add_argument("file")
    d.add_argument("-o", "--out", help="出力先（省略時は標準出力）")
    d.add_argument("--password")

    e = sub.add_parser("encrypt", help="本文を詰め直して暗号化HTMLを更新する")
    e.add_argument("file", help="更新する暗号化HTML（外殻と鍵をここから引き継ぐ）")
    e.add_argument("plaintext", help="差し込む本文HTML")
    e.add_argument("--password")
    e.add_argument("-o", "--out", help="出力先（省略時は file を上書き）")

    sub.add_parser("selftest", help="パスワード不要のラウンドトリップ検証")

    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()

    try:
        html = open(a.file, encoding="utf-8").read()
        pw = get_password(a.password)

        if a.cmd == "decrypt":
            plain = decrypt_html(html, pw)
            if a.out:
                open(a.out, "w", encoding="utf-8").write(plain)
                print(f"復号: {a.file} → {a.out}（{len(plain):,} 文字）", file=sys.stderr)
            else:
                sys.stdout.write(plain)
        else:
            plain = open(a.plaintext, encoding="utf-8").read()
            out_html = encrypt_html(html, plain, pw)
            dest = a.out or a.file
            open(dest, "w", encoding="utf-8").write(out_html)
            print(f"再暗号化: {a.plaintext} → {dest}（{len(plain):,} 文字）", file=sys.stderr)
    except ArchiveError as err:
        print(f"エラー: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
