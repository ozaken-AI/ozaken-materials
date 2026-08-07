#!/usr/bin/env python3
"""全資料にブロック間の余白ルールを一括適用する。

デザインシステムでは .figure と .take が margin-bottom を持たず、
.cards / .two-col / .stepper / .stats は margin をまったく持たない。
そのためこれらが隣り合うと必ず詰まる。ページ個別ではなく、
最後の </style> の直前に共通ルールを差し込んで一括で直す。
"""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oz_root
import lockbox

ROOT = oz_root.root(HERE)
PW = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
MARK = '/* OZ-SPACING v1 */'
MARK_END = '/* /OZ-SPACING */'

CSS = MARK + """
/* ブロック同士が隣り合ったときの余白。デザインシステム側で
   .figure/.take は margin-bottom を持たず、.cards/.two-col/.stepper/.stats は
   margin を持たないため、隣接すると必ず詰まる。ここで一括して空ける。 */
.figure,.take{margin-bottom:0}
.figure + *,.take + *,.deep + *,.cards + *,.two-col + *,
.stepper + *,.stats + *,.note + *,.bare + *{margin-top:2.5rem}
/* 図版の内側も、見出し・キャプションの間を少し広げる */
.fig-title{margin-bottom:1.2rem}
.figure-cap{margin-top:1.3rem}
@media(max-width:640px){
  .figure + *,.take + *,.deep + *,.cards + *,.two-col + *,
  .stepper + *,.stats + *,.note + *,.bare + *{margin-top:1.9rem}
}/* /OZ-SPACING */
"""


def patch(html):
    if MARK in html:
        return None
    i = html.rfind('</style>')
    if i < 0:
        return None
    return html[:i] + CSS + html[i:]


def targets():
    for d in sorted(glob.glob(os.path.join(ROOT, '0*_*'))):
        for f in sorted(glob.glob(os.path.join(d, '*.html'))):
            yield f
    for d in ('AX_Table', 'Training'):        # 裏資料の置き場は2つ
        for f in sorted(glob.glob(os.path.join(ROOT, d, '*.html'))):
            yield f
    for f in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
        yield f


if __name__ == '__main__':
    done = skip = plain = 0
    for f in targets():
        raw = open(f, encoding='utf-8').read()
        if 'OZAKEN-LOCKED2' in raw:
            try:
                inner = lockbox.decrypt(f, PW)
            except BaseException as e:
                print('!! 復号できず:', os.path.relpath(f, ROOT), e)
                continue
            new = patch(inner)
            if new is None:
                skip += 1
                continue
            lockbox.encrypt(f, PW, new)
            assert lockbox.decrypt(f, PW) == new
            done += 1
        else:
            new = patch(raw)
            if new is None:
                skip += 1
                continue
            open(f, 'w', encoding='utf-8').write(new)
            plain += 1
        print('ok', os.path.relpath(f, ROOT))
    print('\n暗号化ページ %d / 平文ページ %d / 対象外・適用済み %d' % (done, plain, skip))
