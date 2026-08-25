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



# ── 色とフォントの規定 ────────────────────────────────
# 資料ごとに見た目がバラつく最大の原因は、その場の思いつきで色を足すこと。
# ここに無い色を使ったら公開させない。役割は references/tokens.md に書いてある。
PALETTE = {
    # 地
    '#f8f7f4', '#1f3864', '#141d35', '#ffffff', '#fff',
    # 面ごとの循環（apply_bgcycle が割り当てる）
    '#eef3fa', '#e7eef8', '#f6f2ea', '#f1eade', '#24446f', '#182c55', '#182a52', '#131c33',
    '#1b3059',
    # 文字
    '#1a1a2e', '#6b7a99', '#d8e4f0',
    # 意味を持つ色
    '#2e5496', '#e23744', '#ff5d6a', '#c9762f', '#2f8f8a',
    # 補助
    '#9fc6f5', '#46c98a', '#eef1f6', '#fde8ea', '#fff8f8',
    # 写真ヒーローの地（AX Table）
    '#0a0f1c', '#8fb0e0',
}
FONT_VARS = {'var(--font-ja-sans)', 'var(--font-ja-serif)', 'var(--font-en)', 'inherit'}


def check_tokens(page):
    """規定外の色・書体を拾う。ここを機械で見ないとレギュレーションは守られない"""
    errs = []
    # HTML実体参照（&#8964; など）は色ではないので、先に落とす
    src = re.sub(r'&#[0-9a-fA-F]+;', '', page)        # 実体参照
    src = re.sub(r'url\(#[^)]*\)', '', src)             # SVGの参照（url(#grad1) など）
    src = re.sub(r'\sid="[^"]*"', '', src)              # id属性
    used = {c.lower() for c in re.findall(r'(?<![&\w])#[0-9a-fA-F]{3,6}\b', src)}
    stray = sorted(c for c in used if c not in PALETTE)
    if stray:
        errs.append('規定外の色: %s（references/tokens.md を参照）' % ' '.join(stray))
    fonts = {f.strip().rstrip(';') for f in re.findall(r'font-family:\s*([^;{}"\']+)', page)}
    bad = sorted(f for f in fonts if f not in FONT_VARS)
    if bad:
        errs.append('規定外の書体: %s（3書体の変数だけを使う）' % ' / '.join(bad))
    return errs


# 表紙の題に使える幅。**実測から決めた値。**
# `.hero > .inner` は max-width:min(1160px,94vw)、左右の余白が24pxずつ、
# 題は clamp(2rem,5.2vw,3.05rem) なので 1440px幅の画面では49px。
# 1112 / 49 ≒ 22.7全角 ── 45（半角単位）まで入るので、1字ぶん余らせて44を上限にする。
# 全資料を描画して測った実際の最大は42だった
HERO_W = 44

# 扉のリード文に使える長さ。**これも実測から決めた値。**
# `.hero-copy` は max-width:620px なので、1行に入るのは38全角ほど。
# 規約は「3〜4行で収める」（page_parts.hero）なので、4行ぶんが上限になる。
# 全資料を描画して測ると、4行に収まっているものの最大が196、
# 5行になってしまうものの最小が252だった。あいだを取って210にする
HERO_COPY_W = 210


def check_hero(page):
    """表紙の題が、テンプレートの形に収まっているか。

    **題は `<br>` で2行まで。**page_parts.hero の規約そのもの。
    3行に割ると、リード文と署名が下へ押し出されて、
    背の低い画面では署名が画面から消える。
    さらに1行が長すぎると勝手に折り返して、結局3行になる。

    幅は字数ではなく**表示幅**で見る。半角の混ざった題（`Gemini Spark` など）を
    字数で切ると、実際には入るものを弾いてしまう。
    """
    from domain_fig import wid
    # 題の class も `hero-title rise d2` のように足されていることがある。
    # 完全一致だと、そういう資料では検査そのものが素通りしていた
    m = re.search(r'<h1 class="[^"]*\bhero-title\b[^"]*">([\s\S]*?)</h1>', page)
    if not m:
        return []
    parts = re.split(r'<br\s*/?>', m.group(1))
    errs = []
    if len(parts) > 2:
        errs.append('表紙の題が%d行: <br>で2行までにする' % len(parts))
    for t in parts:
        t = re.sub(r'<[^>]+>', '', t).replace('&amp;', '&').strip()
        if wid(t) > HERO_W:
            errs.append('表紙の題の1行が長すぎる（表示幅%d / 上限%d）: %s'
                        % (wid(t), HERO_W, t))

    # リード文。**長い扉は、題が正しくても形が崩れる。**
    # 3〜4行で収める規約なので、5行に届く長さは弾く
    # class は `hero-copy rise d4` のように足されていることがある。
    # 完全一致で探すと、そういう資料だけ検査をすり抜ける（実際に1本あった）
    c = re.search(r'<p class="[^"]*\bhero-copy\b[^"]*">([\s\S]*?)</p>', page)
    if c:
        t = re.sub(r'<[^>]+>', '', c.group(1)).replace('&amp;', '&').strip()
        if wid(t) > HERO_COPY_W:
            errs.append('表紙のリード文が長すぎる（表示幅%d / 上限%d）。'
                        '3〜4行に収める。並べたい項目は目次（toc）へ'
                        % (wid(t), HERO_COPY_W))
    return errs


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
    errs += check_hero(page)
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
    # **SVGの文字の中に、HTMLのタグや実体参照を書いてしまっていないか。**
    # 図版の文字は esc() を通るので、<b> は太字にならずそのまま画面に出る。
    # 同じ理由で、&amp; と書くと「&amp;」の6文字がそのまま出てしまう
    #（「セブン&アイ」を「セブン&amp;アイ」と書いて、実際に出た）。
    # 本文カードでは <b> も &amp; も正しいので、SVGの中だけを見る
    leak = set()
    for s_ in svgs:
        leak |= {m for m in re.findall(r'&lt;/?\w+&gt;', s_)}
        leak |= {m for m in re.findall(r'&amp;(?:amp|lt|gt|quot|#\d+);', s_)}
    if leak:
        errs.append('図版の文字にタグ・実体参照が混入: %s'
                    '（SVGの中では太字にできない。素の & をそのまま渡す）'
                    % ' '.join(sorted(leak)))
    errs += check_tokens(page)
    figs = page.count('class="figure"')
    return errs, '本文%d本 / 図版%d点 / SVG%d個' % (len(body), figs, len(svgs))


if __name__ == '__main__':
    page = build(sys.argv[1], sys.argv[2])
    errs, summary = check(page)
    print(('NG: ' + ' / '.join(errs)) if errs else 'OK — ' + summary)
    sys.exit(1 if errs else 0)
