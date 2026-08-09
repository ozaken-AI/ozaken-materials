#!/usr/bin/env python3
"""全資料の本文から、語をさがす。

資料は暗号化されているので、ふつうの grep では中身が見えない。
新しい資料を書く前に「この話は、もうどこかで書いていないか」
「あの数字は、ほかの資料でいくつと書いたか」を確かめるための道具。

  OZAKEN_PW=… python3 find.py 暗黙知
  OZAKEN_PW=… python3 find.py 1クレジット --full       # 前後を長めに出す
  OZAKEN_PW=… python3 find.py 予算 --in 05_drive        # 置き場所でしぼる
  OZAKEN_PW=… python3 find.py ハルシネーション --heads   # 見出しだけを出す

見出しの一覧が欲しいだけなら --heads が速い。
どの資料が何を主張しているかを一望できる。
"""
import html as H
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
import registry
from crossref_data import NOT_DOCS

PW = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
SECTION = re.compile(r'<section class="sec-(?:light|navy)"[^>]*>[\s\S]*?</section>')


def plain(html):
    t = re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', '', html)
    t = re.sub(r'<p class="xr-chips">[\s\S]*?</p>', '', t)
    return re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', ' ', t))).strip()


def head_of(sec):
    m = re.search(r'<h2 class="sec-title">([\s\S]*?)</h2>', sec)
    return re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else '（見出し無し）'


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    full = '--full' in sys.argv
    heads = '--heads' in sys.argv
    where = ''
    if '--in' in sys.argv:
        where = sys.argv[sys.argv.index('--in') + 1]
    if not args and not heads:
        sys.exit(__doc__)
    pad = 90 if full else 40

    led = registry.load(PW)
    n_doc = n_hit = 0
    for f in registry.docs():
        rel = os.path.relpath(f, registry.ROOT)
        if os.path.basename(f) in NOT_DOCS or (where and where not in rel):
            continue
        html = lockbox.decrypt(f, PW)
        title = (led.get(rel, {}).get('title') or rel).split('｜')[0].strip()

        if heads and not args:
            print('\n■ %s\n   %s' % (title, rel))
            for m in SECTION.finditer(html):
                print('     ・%s' % head_of(m.group(0)))
            n_doc += 1
            continue

        found = []
        for m in SECTION.finditer(html):
            sec = m.group(0)
            txt = plain(sec)
            for word in args:
                for hit in re.finditer(re.escape(word), txt):
                    s = max(0, hit.start() - pad)
                    frag = txt[s:hit.end() + pad]
                    found.append((head_of(sec), word, frag))
                    break            # 1セクション1語につき1つで足りる
        if not found:
            continue
        n_doc += 1
        n_hit += len(found)
        print('\n■ %s\n   %s' % (title, rel))
        for head, word, frag in found:
            print('   ├ %s' % head[:56])
            if not heads:
                print('   │   …%s…' % frag.replace(word, '【%s】' % word))
    print('\n%d 本の資料 / %d 箇所' % (n_doc, n_hit))


if __name__ == '__main__':
    main()
