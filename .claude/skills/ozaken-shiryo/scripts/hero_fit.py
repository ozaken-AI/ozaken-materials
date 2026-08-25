#!/usr/bin/env python3
"""扉に置く題とリード文が、テンプレートに収まるかを、書く前に測る。

表紙は投影して最初に映る一枚で、題・リード文・署名が1画面に収まって
初めて成立する。どれかが長いと下の要素が画面の外へ押し出される。
`publish.py` は公開の直前に弾くが、そこで気づくと本文まで書いたあとになる。
**書いている途中で測れるようにしておく。**

長さは字数ではなく**表示幅**で見る（全角2・半角1）。
`Gemini Spark` のような半角の混ざった題を字数で切ると、
実際には入るものまで弾いてしまう。

  python3 hero_fit.py "AIエージェントの教科書" "小売はどう変わるのか"
  python3 hero_fit.py "題の1行目" "2行目" --copy "リード文の全文"
  python3 hero_fit.py --copy "リード文だけ 測りたいとき"
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_page import HERO_W, HERO_COPY_W
from domain_fig import wid


def bar(w, lim, n=40):
    """収まり具合を目で見る。上限を越えた分は別の記号で伸ばす。"""
    full = min(w, lim) * n // lim
    over = max(0, (w - lim) * n // lim)
    return '█' * full + '░' * (n - full) + '!' * min(over, 12)


def report(label, text, lim):
    w = wid(text)
    ok = w <= lim
    print('%s  %3d / %3d  %s %s' % (label, w, lim, bar(w, lim), 'OK' if ok else 'NG'))
    if not ok:
        print('      %d ぶん長い（全角%.1f字）' % (w - lim, (w - lim) / 2))
    return ok


def main(argv):
    lines, copy = [], None
    i = 0
    while i < len(argv):
        if argv[i] == '--copy':
            copy = argv[i + 1]
            i += 2
        else:
            lines.append(argv[i])
            i += 1

    ok = True
    if lines:
        if len(lines) > 2:
            print('題が%d行: <br>で2行までにする' % len(lines))
            ok = False
        for n, t in enumerate(lines, 1):
            ok &= report('題 %d行目 ' % n, t, HERO_W)
    if copy is not None:
        ok &= report('リード文  ', copy, HERO_COPY_W)
        if wid(copy) > HERO_COPY_W:
            print('      並べたい項目は、リード文ではなく目次（toc）へ')
    if not lines and copy is None:
        sys.exit(__doc__)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
