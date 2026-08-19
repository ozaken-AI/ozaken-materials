#!/usr/bin/env python3
"""セクションごとに背景色を替える。

講演で1枚ずつ送っていくと、同じ2色が交互に出るだけでは
「いま何枚目か」が分からなくなり、途中から景色が変わらない資料に見える。
明るい面・暗い面という骨格は保ったまま、その中で色味を3段ずつ循環させると、
スクロールするたびに景色が変わり、聴講者が現在地を掴みやすくなる。

各セクションに data-bg="1|2|3" を順に振り、CSSはその属性で色を決める。
nth-child に頼らないのは、あとから節を足しても割り当てが崩れないようにするため。
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oz_root
import lockbox

ROOT = oz_root.root(HERE)
PW = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
MARK = '/* OZ-BG v1 */'
MARK_END = '/* /OZ-BG */'

CSS = MARK + """
/* ══ 面ごとの背景。明るい面・暗い面それぞれの中で3段を循環させる ══ */
/* **明るい面は、全部おなじ青系で回す。**
   以前は3番目だけ生成り（#f6f2ea）で、そこだけ紙の色が変わって見えた。
   面ごとに紙が変わると、資料をまたいだときに「別のサイト」に見える */
.sec-light[data-bg="1"]{background:var(--paper)}
.sec-light[data-bg="2"]{background:linear-gradient(178deg,#eef3fa 0%,#e7eef8 100%)}
.sec-light[data-bg="3"]{background:linear-gradient(178deg,#e7eef8 0%,#eef3fa 100%)}
.sec-navy[data-bg="1"]{background:linear-gradient(172deg,#1f3864 0%,#1b3059 100%)}
.sec-navy[data-bg="2"]{background:linear-gradient(172deg,#24446f 0%,#182c55 100%)}
.sec-navy[data-bg="3"]{background:linear-gradient(172deg,#182a52 0%,#131c33 100%)}
/* 面の変わり目に細い線を置き、投影で「画面が切り替わった」ことを分かりやすくする */
.sec-light[data-bg]+.sec-navy[data-bg],
.sec-navy[data-bg]+.sec-light[data-bg]{position:relative}
.sec-light[data-bg]+.sec-navy[data-bg]::before,
.sec-navy[data-bg]+.sec-light[data-bg]::before{content:"";position:absolute;
  top:0;left:0;right:0;height:2px;pointer-events:none;
  background:linear-gradient(90deg,transparent,rgba(226,55,68,.55),transparent)}/* /OZ-BG */
"""


def patch(html):
    if MARK in html:
        return None
    i = html.rfind('</style>')
    if i < 0:
        return None
    html = html[:i] + CSS + html[i:]

    # 明るい面・暗い面それぞれで、独立に1→2→3を回す。
    # 同じ側が続いても色が変わり、隣り合う面は必ず別の色になる
    n = {'sec-light': 0, 'sec-navy': 0}

    def tag(m):
        cls = m.group(1)
        if 'data-bg' in m.group(0):
            return m.group(0)
        n[cls] += 1
        return '<section class="%s" data-bg="%d"' % (cls, (n[cls] - 1) % 3 + 1)

    return re.sub(r'<section class="(sec-light|sec-navy)"', tag, html)


def targets():
    # **分類フォルダは2桁。0 始まりとは限らない。**
    # 分類が10を超えた日に、ここが '0*_*' のままだと新しい分類が丸ごと外れる
    for d in sorted(glob.glob(os.path.join(ROOT, '[0-9][0-9]_*'))):
        for f in sorted(glob.glob(os.path.join(d, '*.html'))):
            yield f
    for d in oz_root.BACKSTAGE_DIRS:
        for f in sorted(glob.glob(os.path.join(ROOT, d, '*.html'))):
            yield f
    for f in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
        if os.path.basename(f) not in ('index.html', 'ask.html'):
            yield f


if __name__ == '__main__':
    done = skip = 0
    for f in targets():
        raw = open(f, encoding='utf-8').read()
        enc = 'OZAKEN-LOCKED2' in raw
        inner = lockbox.decrypt(f, PW) if enc else raw
        new = patch(inner)
        if new is None:
            skip += 1
            continue
        if enc:
            lockbox.encrypt(f, PW, new)
            assert lockbox.decrypt(f, PW) == new
        else:
            open(f, 'w', encoding='utf-8').write(new)
        done += 1
    print('背景の循環を適用 %d ページ / 適用済み %d' % (done, skip))
