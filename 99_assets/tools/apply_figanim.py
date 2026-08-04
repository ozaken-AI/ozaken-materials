#!/usr/bin/env python3
"""既存の資料の図版に、動きを与える。

スタイル側には a-fade / a-pop / a-grow / a-draw の仕掛けが最初からあり、
画面に入ったら .anim-on が付く仕組みも動いている。
足りていなかったのは、SVGの各要素に印と遅延を振ることだけ。

新しく作る資料は domain_fig._fig() が自動で振るが、
すでに出来上がっている資料は中身が固まっているので、ここで後から振る。
対象は .figure と .hero-glyph の中のSVGだけ。
ファーストビューの背景SVGは別の演出を持っているので触らない。
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
from domain_fig import _animate

ROOT = os.environ.get('OZAKEN_ROOT') or os.path.dirname(os.path.dirname(HERE))
PW = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
MARK = '<!-- OZ-FIGANIM v1 -->'

BLOCK = re.compile(
    r'(<div class="(?:figure|hero-glyph)[^"]*">[\s\S]*?)(<svg[\s\S]*?</svg>)')


def patch(html):
    if MARK in html:
        return None
    n = [0]

    def one(m):
        head, svg = m.group(1), m.group(2)
        if 'a-fade' in svg or 'a-grow' in svg:      # すでに動きを持っている図は触らない
            return m.group(0)
        n[0] += 1
        return head + _animate(svg)

    out = BLOCK.sub(one, html)
    if not n[0]:
        return None
    i = out.rfind('</body>')
    return out[:i] + MARK + '\n' + out[i:] if i > 0 else out + MARK


def targets():
    for d in sorted(glob.glob(os.path.join(ROOT, '0*_*'))):
        for f in sorted(glob.glob(os.path.join(d, '*.html'))):
            yield f
    for f in sorted(glob.glob(os.path.join(ROOT, 'AX_Table', '*.html'))):
        yield f
    for f in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
        if os.path.basename(f) not in ('index.html', 'ask.html'):
            yield f


if __name__ == '__main__':
    done = skip = figs = 0
    for f in targets():
        raw = open(f, encoding='utf-8').read()
        enc = 'OZAKEN-LOCKED2' in raw
        inner = lockbox.decrypt(f, PW) if enc else raw
        new = patch(inner)
        if new is None:
            skip += 1
            continue
        figs += new.count('a-fade')
        if enc:
            lockbox.encrypt(f, PW, new)
            assert lockbox.decrypt(f, PW) == new
        else:
            open(f, 'w', encoding='utf-8').write(new)
        done += 1
    print('図版に動きを付けた %d ページ / 対象外・適用済み %d' % (done, skip))
