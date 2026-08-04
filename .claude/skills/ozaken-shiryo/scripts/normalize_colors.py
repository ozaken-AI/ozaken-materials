#!/usr/bin/env python3
"""規定外の色を、いちばん近い規定色に寄せる。

資料ごとに見た目がばらつく最大の原因は、その場の思いつきで足された色。
「ほぼ同じだが少しだけ違う水色」が7種類あると、並べたときに揃って見えない。

  OZAKEN_PW=… python3 normalize_colors.py --dry   # 何をどう置き換えるかだけ出す
  OZAKEN_PW=… python3 normalize_colors.py         # 実際に置き換える

近いものは機械的に寄せる。遠いものは色の系統で判断する
（暖色はAMBER、赤紫は赤、青系は明るさで段を選ぶ）。
**置き換えたら必ずレンダリングして見ること。** 濃淡が反転していないかは目でしか分からない。
"""
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
import oz_root
import registry
from build_page import PALETTE
from crossref_data import NOT_DOCS

PW = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
ROOT = oz_root.root(HERE)
DRY = '--dry' in sys.argv
SNAP = 28.0                       # これより近ければ、系統を考えず寄せる

# 青系の段。暗い順に、明るさで選ぶ
BLUES = [(55, '#141d35'), (75, '#24446f'), (105, '#2e5496'),
         (150, '#6b7a99'), (185, '#8fb0e0'), (215, '#d8e4f0'), (999, '#eef3fa')]


def rgb(h):
    h = h.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


PAL = [(p, rgb(p)) for p in PALETTE if len(p) in (4, 7)]


def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def target(c):
    """この色を、どの規定色に寄せるか"""
    r, g, b = rgb(c)
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    best, d = min(((p, dist(rgb(c), v)) for p, v in PAL), key=lambda x: x[1])
    if d < SNAP:
        return best, 'near'
    # 遠いものは系統で決める。近さより「意味」を優先する。
    # chroma（いちばん強い成分と弱い成分の差）で、鮮やかな色と淡い色を分ける。
    # 明るさだけで判断すると、鮮やかな山吹色が「淡いベージュ」に飛ばされる
    chroma = max(r, g, b) - min(r, g, b)
    if lum < 40:                                    # ほぼ黒。本文の墨に寄せる
        return '#1a1a2e', 'ink'
    if r - b > 40 and r >= g >= b:                  # 暖色
        return ('#c9762f' if chroma >= 55 or lum < 170 else '#f1eade'), 'warm'
    if r > g and r > b and abs(g - b) < 26:         # 赤・ピンク
        return ('#ff5d6a' if chroma >= 70 else '#fde8ea'), 'red'
    if chroma < 45 and 55 <= lum < 180:             # 青みの灰。説明文の色に寄せる
        return '#6b7a99', 'grey'
    for lim, tok in BLUES:                          # 青は明るさで段を選ぶ
        if lum < lim:
            return tok, 'blue'
    return '#eef3fa', 'blue'


def strays(html):
    src = re.sub(r'&#[0-9a-fA-F]+;', '', html)
    src = re.sub(r'url\(#[^)]*\)', '', src)
    src = re.sub(r'\sid="[^"]*"', '', src)
    used = {c.lower() for c in re.findall(r'(?<![&\w])#[0-9a-fA-F]{3,6}\b', src)}
    return sorted(c for c in used if c not in PALETTE)


def main():
    plan, hit = {}, Counter()
    docs = []
    for f in registry.docs():
        if os.path.basename(f) in NOT_DOCS:
            continue
        html = lockbox.decrypt(f, PW)
        st = strays(html)
        if st:
            docs.append((f, html, st))
            for c in st:
                hit[c] += 1
                if c not in plan:
                    plan[c] = target(c)

    print('規定外の色 %d 種 / %d 本の資料\n' % (len(plan), len(docs)))
    print('%-10s %-5s %-10s %s' % ('元', '本数', '寄せ先', '根拠'))
    for c, n in hit.most_common():
        t, why = plan[c]
        print('%-10s %-5d %-10s %s' % (c, n, t, why))
    if DRY:
        print('\n--dry なので書き換えていません。')
        return

    n_doc = n_rep = 0
    for f, html, st in docs:
        out = html
        for c in st:
            t = plan[c][0]
            # 3桁表記も同じ色を指しているので、両方まとめて置き換える
            pat = re.compile(re.escape(c), re.I)
            out, k = pat.subn(t, out)
            n_rep += k
        if out == html:
            continue
        lockbox.encrypt(f, PW, out)
        assert lockbox.decrypt(f, PW) == out
        n_doc += 1
    print('\n%d 本の資料で %d 箇所を置き換えました。'
          '**必ずレンダリングして目で見てください。**' % (n_doc, n_rep))


if __name__ == '__main__':
    main()
