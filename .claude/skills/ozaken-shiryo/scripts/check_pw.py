#!/usr/bin/env python3
"""資料のパスワードを一覧で確かめる。

暗号化の作りとして、パスワードそのものは取り出せない（PBKDF2 20万回＋AES-GCM）。
できるのは「この文字列でこの資料が開くか」を試すことだけなので、
  1) 各資料に個別パスワードが設定されているか（鍵の本数）を一覧にする
  2) 候補の文字列を渡すと、どの資料が開くかを総当たりで突き合わせる
の2つを用意した。

  使い方:
    python3 check_pw.py                     # 鍵の本数だけを一覧表示
    python3 check_pw.py pw1 pw2 pw3         # 候補を直接渡す
    python3 check_pw.py -f candidates.txt   # 1行1件のファイルから読む

  マスターパスワードは環境変数で渡す（一覧から除くためだけに使う）:
    OZAKEN_PW=… python3 check_pw.py -f candidates.txt

  必要なもの: pip install cryptography
"""
import base64
import glob
import hashlib
import json
import os
import re
import sys
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oz_root

ROOT = oz_root.root()
MASTER = os.environ.get('OZAKEN_PW', '')      # 環境変数で渡す。ここには書かない
ITER = 200000

# 道具のページ。**マスターだけで開く。共通パスワードを付けない。**
# 共通パスワードは資料を配るためのもので、配った相手にこの3枚まで開かれると、
# 全資料の一覧・裏資料の置き場・全パスワードが渡ってしまう
TOOLS = ('passwords.html', 'backstage.html', 'matrix.html')


def docs():
    out = []
    # **分類フォルダは2桁。0 始まりとは限らない。**
    # 分類が10を超えた日に、ここが '0*_*' のままだと新しい分類が丸ごと外れる
    for d in sorted(glob.glob(os.path.join(ROOT, '[0-9][0-9]_*'))):
        out += sorted(glob.glob(os.path.join(d, '*.html')))
    out += sorted(glob.glob(os.path.join(ROOT, 'AX_Table', '*.html')))
    for d in oz_root.BACKSTAGE_DIRS[1:]:      # AX_Table は上で拾っている
        out += sorted(glob.glob(os.path.join(ROOT, d, '*.html')))
    out += [f for f in sorted(glob.glob(os.path.join(ROOT, '*.html')))
            if os.path.basename(f) not in ('index.html', 'ask.html')]
    return [f for f in out if 'OZAKEN-LOCKED2' in open(f, encoding='utf-8').read(64)]


def wrappers(path):
    raw = open(path, encoding='utf-8').read()
    m = re.search(r'W=(\[.*?\]),ITER', raw, re.S)
    return json.loads(m.group(1)) if m else []


def opens(path, pw):
    """pw でこの資料が開くか。鍵の取り出しだけ試せば十分なので本文は復号しない"""
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError:
        return None
    for w in wrappers(path):
        salt = base64.b64decode(w['s'])
        key = hashlib.pbkdf2_hmac('sha256', pw.encode(), salt, ITER, 32)
        try:
            AESGCM(key).decrypt(base64.b64decode(w['iv']), base64.b64decode(w['ct']), None)
            return True
        except Exception:
            pass
    return False


def _job(args):
    path, pw = args
    return path, pw, opens(path, pw)


def audit(files):
    """道具のページに、マスター以外の鍵が付いていないかを毎回見る。
    ここが崩れると、共通パスワードを渡した相手にアーカイブ全体が渡る"""
    bad = [os.path.relpath(f, ROOT) for f in files
           if os.path.basename(f) in TOOLS and len(wrappers(f)) != 1]
    if bad:
        print('!! 道具のページに余分な鍵が付いています: %s' % ' / '.join(bad))
        print('   マスター以外を外してください:')
        print('   lockbox.remove_password(パス, マスター, 外す鍵)\n')
    else:
        print('道具のページ（%s）は、マスターのみで開きます\n'
              % ' / '.join(TOOLS))


def main():
    args = sys.argv[1:]
    cands = []
    if args and args[0] == '-f':
        cands = [l.strip() for l in open(args[1], encoding='utf-8') if l.strip()]
    else:
        cands = args

    files = docs()
    print('暗号化された資料: %d 本\n' % len(files))
    audit(files)

    if not cands:
        print('%-52s %s' % ('資料', '鍵'))
        print('-' * 62)
        solo = []
        for f in files:
            n = len(wrappers(f))
            rel = os.path.relpath(f, ROOT)
            print('%-52s %s' % (rel[:52], 'マスターのみ' if n == 1 else '個別あり（%d本）' % n))
            if n == 1:
                solo.append(rel)
        print('\n個別パスワード無し（マスターのみで開く）: %d 本' % len(solo))
        print('候補を渡すと、どれがどの資料を開くか突き合わせます:')
        print('  python3 check_pw.py 候補1 候補2 …')
        return

    print('候補 %d 件を %d 本の資料に突き合わせます…\n' % (len(cands), len(files)))
    jobs = [(f, pw) for f in files for pw in cands]
    hit = {}
    with ProcessPoolExecutor() as ex:
        for path, pw, ok in ex.map(_job, jobs, chunksize=4):
            if ok:
                hit.setdefault(os.path.relpath(path, ROOT), []).append(pw)

    for f in files:
        rel = os.path.relpath(f, ROOT)
        got = [p for p in hit.get(rel, []) if p != MASTER]
        n = len(wrappers(f))
        if n > 1 and not got:
            mark = '× 個別パスワードが候補の中に無い'
        elif got:
            mark = '○ ' + ' / '.join(got)
        else:
            mark = '－ マスターのみ'
        print('%-46s %s' % (rel[:46], mark))

    unused = [p for p in cands if p != MASTER and not any(p in v for v in hit.values())]
    if unused:
        print('\nどの資料も開かなかった候補: ' + ' / '.join(unused))


if __name__ == '__main__':
    main()
