#!/usr/bin/env python3
"""OZAKEN-LOCKED2 エンベロープ暗号ページの復号／再暗号化ユーティリティ。

書式:
  var CT="<base64>",IVC="<base64>",W=[{s,iv,ct},...],ITER=200000,KEY="ozaken_archive_pw";

CT = 本文HTML を content key (32byte) + AES-GCM(IVC) で暗号化したもの。
W  = content key を各パスワード由来鍵(PBKDF2-SHA256, ITER)でラップしたもの。
再暗号化では content key と W はそのまま流用し、CT と IVC だけ差し替える。
"""
import base64
import json
import os
import re
import sys

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

VARS_RE = re.compile(
    r'var CT="(?P<ct>[^"]+)",IVC="(?P<ivc>[^"]+)",W=(?P<w>\[.*?\]),ITER=(?P<iter>\d+),KEY="(?P<key>[^"]+)";'
)


def b64d(s):
    return base64.b64decode(s)


def b64e(b):
    return base64.b64encode(b).decode()


def parse(html):
    m = VARS_RE.search(html)
    if not m:
        raise SystemExit("暗号ヘッダを検出できません")
    return m


def content_key(m, pw):
    for w in json.loads(m.group("w")):
        kdf = PBKDF2HMAC(algorithm=SHA256(), length=32, salt=b64d(w["s"]),
                         iterations=int(m.group("iter")))
        key = kdf.derive(pw.encode())
        try:
            return AESGCM(key).decrypt(b64d(w["iv"]), b64d(w["ct"]), None)
        except Exception:
            continue
    raise SystemExit("パスワードが違います（どのラップ鍵も解けません）")


def decrypt(path, pw):
    html = open(path, encoding="utf-8").read()
    m = parse(html)
    ck = content_key(m, pw)
    pt = AESGCM(ck).decrypt(b64d(m.group("ivc")), b64d(m.group("ct")), None)
    return pt.decode("utf-8")


def encrypt(path, pw, plaintext, out_path=None):
    html = open(path, encoding="utf-8").read()
    m = parse(html)
    ck = content_key(m, pw)
    iv = os.urandom(12)
    ct = AESGCM(ck).encrypt(iv, plaintext.encode("utf-8"), None)
    new_vars = 'var CT="%s",IVC="%s",W=%s,ITER=%s,KEY="%s";' % (
        b64e(ct), b64e(iv), m.group("w"), m.group("iter"), m.group("key"))
    out = html[: m.start()] + new_vars + html[m.end():]
    open(out_path or path, "w", encoding="utf-8").write(out)


if __name__ == "__main__":
    cmd, path, pw = sys.argv[1], sys.argv[2], os.environ["OZ_PW"]
    if cmd == "dec":
        sys.stdout.write(decrypt(path, pw))
    elif cmd == "enc":
        encrypt(path, pw, open(sys.argv[3], encoding="utf-8").read())
        print("re-encrypted:", path)


def create(template_path, plaintext, out_path, passwords):
    """既存のロック画面テンプレートを流用して、新規のエンベロープ暗号ページを作る。"""
    shell = open(template_path, encoding='utf-8').read()
    m = parse(shell)
    iters = int(m.group('iter'))
    ck = os.urandom(32)
    W = []
    for pw in passwords:
        salt, iv = os.urandom(16), os.urandom(12)
        kdf = PBKDF2HMAC(algorithm=SHA256(), length=32, salt=salt, iterations=iters)
        wrapped = AESGCM(kdf.derive(pw.encode())).encrypt(iv, ck, None)
        W.append({"s": b64e(salt), "iv": b64e(iv), "ct": b64e(wrapped)})
    ivc = os.urandom(12)
    ct = AESGCM(ck).encrypt(ivc, plaintext.encode('utf-8'), None)
    new_vars = 'var CT="%s",IVC="%s",W=%s,ITER=%d,KEY="%s";' % (
        b64e(ct), b64e(ivc), json.dumps(W), iters, m.group('key'))
    open(out_path, 'w', encoding='utf-8').write(shell[:m.start()] + new_vars + shell[m.end():])
