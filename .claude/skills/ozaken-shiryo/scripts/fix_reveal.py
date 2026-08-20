#!/usr/bin/env python3
"""出現の判定を、要素の高さに依存しない形に直す。

**背の高い塊が、永久に出てこなくなっていた。**

`[data-reveal]` は「要素の10%が画面に入ったら表示」（threshold: 0.1）で
判定していた。ところがこれは、**要素が画面の10倍より高いと絶対に満たされない**。

  資料アーカイブの塊  スマートフォンで 10,423px
  その10%             1,042px
  画面の高さ           844px   → 永久に届かない

分類が9から11に増え、資料も足したところで、この線を越えた。
玄関の資料一覧が、スマートフォンでだけ真っ白になっていた。
パソコンでは多段の格子になって低くなるので、気づけない。

**高さで測るのをやめる。** 下端から少し入ったら出す、に変える。

  { threshold: 0.1 }  →  { threshold: 0, rootMargin: '0px 0px -12% 0px' }

これなら要素の上端が画面の下から12%のところへ来た時点で出るので、
要素が何ページ分あっても関係ない。図版の判定（0.18）も同じ理由で直す。

  OZAKEN_PW=マスター python3 fix_reveal.py         # 直す（冪等）
  OZAKEN_PW=マスター python3 fix_reveal.py list    # どれが古いかを見るだけ
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
import oz_root
import registry

ROOT = oz_root.root(HERE)

# (古い書き方, 新しい書き方, 何の判定か)
SWAPS = [
    ("}, { threshold: 0.1 });",
     "}, { threshold: 0, rootMargin: '0px 0px -12% 0px' });",
     '本文の出現'),
    ("}, { threshold: 0.18 });",
     "}, { threshold: 0, rootMargin: '0px 0px -18% 0px' });",
     '図版の組み上がり'),
]


def patch(html):
    n = 0
    for old, new, _ in SWAPS:
        c = html.count(old)
        if c:
            html = html.replace(old, new)
            n += c
    return html, n


def main():
    pw = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
    show = len(sys.argv) > 1 and sys.argv[1] == 'list'
    done = total = 0

    # 玄関は暗号化されていないので、別に扱う
    idx = os.path.join(ROOT, 'index.html')
    src = open(idx, encoding='utf-8').read()
    new, n = patch(src)
    if n:
        total += n
        print('  %-46s %d か所' % ('index.html', n))
        if not show:
            open(idx, 'w', encoding='utf-8').write(new)
            done += 1

    for f in registry.docs():
        rel = os.path.relpath(f, ROOT)
        h = lockbox.decrypt(f, pw)
        new, n = patch(h)
        if not n:
            continue
        total += n
        print('  %-46s %d か所' % (rel, n))
        if show:
            continue
        lockbox.encrypt(f, pw, new)
        assert lockbox.decrypt(f, pw) == new
        done += 1

    print('古い判定 %d か所 / %s %d 本'
          % (total, '見つかった' if show else '直した', done))


if __name__ == '__main__':
    main()
