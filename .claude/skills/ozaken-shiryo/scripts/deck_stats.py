#!/usr/bin/env python3
"""資料を、面ごとに数えて並べる。

「単調かどうか」は感覚の話に見えて、かなりの部分は数えれば分かる。
同じかたちの図が続いていないか、文字量が偏っていないか、赤を撒いていないか。
評価するときの材料を、先に機械で出しておくための道具。

  OZAKEN_PW=… python3 deck_stats.py 03_tools/foo.html

判断はしない。並べるだけ。読むのは人（か、評価スキル）の仕事。
"""
import html as H
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockbox
import oz_root

PW = os.environ.get('OZAKEN_PW') or sys.exit('OZAKEN_PW を設定してください')
ROOT = oz_root.root(HERE)

SECTION = re.compile(r'<section class="sec-(light|navy)"([^>]*)>([\s\S]*?)</section>')
RED = ('#e23744', '#ff5d6a', 'text-red', 'var(--red')


def text_of(x):
    x = re.sub(r'<svg[\s\S]*?</svg>', ' ', x)
    return re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', ' ', x))).strip()


def shape(svg):
    """図のかたちの指紋。何が多いかで、だいたいの型が分かる"""
    c = Counter()
    for tag in ('rect', 'circle', 'path', 'line', 'text', 'polygon', 'ellipse'):
        c[tag] = len(re.findall(r'<%s[\s>]' % tag, svg))
    kind = []
    if c['rect'] >= 4:
        kind.append('箱')
    if c['circle'] >= 3:
        kind.append('丸')
    if c['path'] >= 3 or c['line'] >= 3:
        kind.append('線')
    if 'marker-end' in svg:
        kind.append('矢印')
    if re.search(r'<rect[^>]*height="(\d{2,})"', svg) and c['rect'] >= 6:
        kind.append('棒')
    return '+'.join(kind) or '—', c


def main():
    rel = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
    path = os.path.join(ROOT, rel)
    html = lockbox.decrypt(path, PW)

    title = re.search(r'<title>(.*?)</title>', html, re.S)
    hero = re.search(r'<h1 class="hero-title">([\s\S]*?)</h1>', html)
    print('■ %s' % (H.unescape(title.group(1)).split('|')[0].strip() if title else rel))
    if hero:
        print('   表紙: %s' % text_of(hero.group(1))[:70])

    rows, shapes, bgs, faces = [], [], [], []
    total_red = 0
    for i, m in enumerate(SECTION.finditer(html), 1):
        face, attrs, body = m.group(1), m.group(2), m.group(3)
        bg = (re.search(r'data-bg="(\d)"', attrs) or [None, '-'])[1]
        head = re.search(r'<h2 class="sec-title">([\s\S]*?)</h2>', body)
        head = text_of(head.group(1)) if head else '(見出し無し)'
        txt = text_of(body)
        cards = len(re.findall(r'class="[^"]*\bcard\b', body))
        takes = len(re.findall(r'class="[^"]*\btake\b', body))
        figs = re.findall(r'<svg[\s\S]*?</svg>', body)
        red = sum(body.count(r) for r in RED)
        total_red += red
        figtitle = re.search(r'<p class="fig-title">([\s\S]*?)</p>', body)
        kinds = [shape(s)[0] for s in figs]
        rows.append((i, face, bg, head, len(txt), cards, takes, len(figs),
                     '/'.join(kinds) or '—', red,
                     text_of(figtitle.group(1))[:34] if figtitle else ''))
        shapes.append('/'.join(kinds) or '—')
        bgs.append('%s%s' % (face[0].upper(), bg))
        faces.append(face)

    print('\n%-3s %-5s %-3s %-5s %-3s %-3s %-3s %-9s %s' %
          ('#', '面', '背', '文字', 'カ', '引', '図', 'かたち', '見出し'))
    print('-' * 96)
    for (i, face, bg, head, n, cards, takes, nf, kinds, red, ft) in rows:
        print('%-3d %-5s %-3s %-5d %-3d %-3d %-3d %-9s %s' %
              (i, face, bg, n, cards, takes, nf, kinds[:9], head[:34]))
        if ft:
            print('%s└ %s' % (' ' * 36, ft))

    print('\n── 数えたもの ──')
    print('本文セクション %d 本（%s）' % (len(rows), ' '.join(bgs)))
    lens = [r[4] for r in rows]
    if lens:
        print('文字量  最小 %d / 最大 %d / 平均 %d  ← 差が3倍を超えると、面ごとの重さがばらつく'
              % (min(lens), max(lens), sum(lens) // len(lens)))
    nofig = [r[0] for r in rows if r[7] == 0]
    if nofig:
        print('図版が無い面: %s  ← 投影すると文字の壁になる' % nofig)
    same = [(rows[i][0], shapes[i]) for i in range(1, len(shapes))
            if shapes[i] == shapes[i - 1] and shapes[i] != '—']
    if same:
        print('直前と同じかたちの図が続く面: %s'
              % ' '.join('%d(%s)' % s for s in same))
    c = Counter(s for s in shapes if s != '—')
    if c:
        print('かたちの分布: %s' % ' / '.join('%s×%d' % kv for kv in c.most_common()))
        top, n = c.most_common(1)[0]
        if n >= max(3, len(rows) // 2):
            print('  ← 「%s」に寄っている。半分以上が同じ見え方だと、送っても景色が変わらない' % top)
    print('赤の使用 %d 箇所（1面に1箇所までが目安。%d 面ある）' % (total_red, len(rows)))
    # check() と同じ数え方。最後の1本は締めなので「本文」には数えない
    body_n = len(faces) - 1
    if faces and (faces[-1] != 'navy' or body_n % 2 == 0
                  or not all(a != b for a, b in zip(faces, faces[1:]))):
        print('⚠ 並びが規約から外れている（本文は奇数本・交互・末尾navy）')


if __name__ == '__main__':
    main()
