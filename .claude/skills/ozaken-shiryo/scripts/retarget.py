#!/usr/bin/env python3
"""配信先を引っ越したときに、焼き込まれた古いURLを全部書き換える。

**URLは、いろいろなところに焼き込まれている。**
QRの升目（SVGとして資料の中）、共有カードの og:url、
玄関に出している文字、配布PDFの奥付。実行時に外を見ない作りなので、
引っ越したら焼き直すしかない。それを1回で通す。

  1. oz_site.py の SITE を新しいURLに直す
  2. OZAKEN_PW=マスター python3 retarget.py 旧URL          # 何が変わるか見る
  3. OZAKEN_PW=マスター python3 retarget.py 旧URL --apply  # 書き換える

そのあと QR と共有カードを焼き直すところまで、この道具が面倒を見る。

  例: OZAKEN_PW=… python3 retarget.py https://ozaken-ai.github.io/ozaken-materials/ --apply

**カスタムドメインを当てると、パスの階層が1つ減る。**
`.../ozaken-materials/05_drive/foo.html` が `.../05_drive/foo.html` になる。
資料の中のリンクはすべて相対で書いてあるので、そこは触らなくてよい。
"""
import glob
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
import oz_root
import registry
from oz_site import SITE, bare

ROOT = oz_root.root(HERE)

# 暗号の外にある、URLを焼き込んでいるファイル
PLAIN = ['index.html', 'ask.html', '404.html', 'console.html', 'backstage.html',
         'matrix.html', 'template.html', 'passwords.html', 'inbox.html']


def swaps(old):
    """置き換えの組。**長いものから当てる。**
    先に短い形（httpsなし）を当てると、長い形の一部だけが置き換わる"""
    return [(old, SITE), (bare(old), bare())]


def rewrite(text, old):
    n = 0
    for a, b in swaps(old):
        c = text.count(a)
        if c:
            text = text.replace(a, b)
            n += c
    return text, n


def main():
    pw = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    old = sys.argv[1]
    if not old.endswith('/'):
        old += '/'
    apply = '--apply' in sys.argv
    if old.rstrip('/') == SITE.rstrip('/'):
        sys.exit('oz_site.py の SITE が、まだ古いURLのままです')

    print('%s\n  → %s\n' % (old, SITE))
    total = files = 0

    # ── 暗号の外 ──────────────────────────────
    for rel in PLAIN + sorted(glob.glob('99_assets/pdf-src/*.py')):
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        src = io.open(path, encoding='utf-8').read()
        new, n = rewrite(src, old)
        if not n:
            continue
        total += n
        files += 1
        print('  %-46s %d か所' % (rel, n))
        if apply:
            io.open(path, 'w', encoding='utf-8').write(new)

    # ── 暗号の中 ──────────────────────────────
    for f in registry.docs():
        rel = os.path.relpath(f, ROOT)
        h = lockbox.decrypt(f, pw)
        new, n = rewrite(h, old)
        if not n:
            continue
        total += n
        files += 1
        print('  %-46s %d か所' % (rel, n))
        if apply:
            lockbox.encrypt(f, pw, new)
            assert lockbox.decrypt(f, pw) == new

    print('\n古いURL %d か所 / %d ファイル' % (total, files))
    if not apply:
        print('書き換えるには --apply を付けてください')
        return

    # **QRは升目として焼き込まれている。** 文字を置き換えても升目は古いまま。
    # 必ず焼き直す
    print('\nQRの升目を焼き直します')
    import apply_qr
    apply_qr.main_refresh() if hasattr(apply_qr, 'main_refresh') else os.system(
        'cd %s && OZAKEN_PW=%s python3 apply_qr.py refresh' % (HERE, pw))
    print('\n共有カードの og:url を入れ直します')
    os.system('cd %s && OZAKEN_PW=%s python3 apply_ogp.py apply' % (HERE, pw))
    print('\n共有カードの画像は、別に焼き直してください:')
    print('  OZAKEN_PW=… python3 apply_ogp.py cards')


if __name__ == '__main__':
    main()
