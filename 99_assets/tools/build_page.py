#!/usr/bin/env python3
"""本文フラグメントから、おざけんWebスタイル準拠の完成ページを組み立てる。

使い方:  python3 build_page.py <body.html> <out.html>
本文フラグメントの先頭に、以下のメタ行を置く（<!--META ... -->）。
  <!--META title=... | desc=... -->
"""
import re
import sys
import pathlib

HERE = pathlib.Path(__file__).parent
STYLE = (HERE / 'tpl_style.html').read_text(encoding='utf-8')
TAIL = (HERE / 'tpl_tail.html').read_text(encoding='utf-8')

HEAD = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | おざけん</title>
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700&family=Shippori+Mincho+B1:wght@400;500;600&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap" rel="stylesheet">
{style}
</head>
<body>
"""

FOOT = """
<footer>
  <p>&copy; 2026 小澤健祐（おざけん）/ 一般社団法人AICX協会 &nbsp;｜&nbsp; <a href="../index.html">← AI資料アーカイブに戻る</a></p>
</footer>
{tail}
</body>
</html>
"""


def build(body_path, out_path):
    src = pathlib.Path(body_path).read_text(encoding='utf-8')
    m = re.match(r'<!--META\s+title=(.*?)\s*\|\s*desc=(.*?)\s*-->\n', src, re.S)
    if not m:
        raise SystemExit('METAコメントがありません')
    title, desc = m.group(1), m.group(2)
    body = src[m.end():]
    page = HEAD.format(title=title, desc=desc, style=STYLE) + body + FOOT.format(tail=TAIL)
    pathlib.Path(out_path).write_text(page, encoding='utf-8')
    return page


def check(page):
    import xml.etree.ElementTree as ET
    errs = []
    if page.count('<table'):
        errs.append('tableタグが混入')
    if page.count('btn-primary') + page.count('btn-secondary'):
        errs.append('CTAボタンが混入')
    order = re.findall(r'<section class="(hero|sec-light|sec-navy)"', page)
    body = order[1:-1]
    if len(body) % 2 == 0:
        errs.append('本文セクションが偶数本: %d' % len(body))
    if not all(a != b for a, b in zip(order, order[1:])):
        errs.append('同じ背景が連続: %s' % order)
    if order[-1] != 'sec-navy':
        errs.append('末尾がネイビーでない')
    if page.count('class="take"') > 2:
        errs.append('takeが3回以上')
    svgs = re.findall(r'<svg[\s\S]*?</svg>', page)
    for i, s in enumerate(svgs):
        try:
            ET.fromstring(s)
        except Exception as e:
            errs.append('SVG%d パース失敗: %s' % (i, e))
    rot = re.findall(r'<text[^>]*rotate[^>]*>([^<]*)</text>', page)
    if any(c in t for t in rot for c in '↑↓←→'):
        errs.append('回転テキストに矢印グリフ')
    ids = re.findall(r'<marker id="([^"]+)"', page)
    if len(ids) != len(set(ids)):
        errs.append('marker id重複: %s' % ids)
    figs = page.count('class="figure"')
    return errs, '本文%d本 / 図版%d点 / SVG%d個' % (len(body), figs, len(svgs))


if __name__ == '__main__':
    page = build(sys.argv[1], sys.argv[2])
    errs, summary = check(page)
    print(('NG: ' + ' / '.join(errs)) if errs else 'OK — ' + summary)
    sys.exit(1 if errs else 0)
