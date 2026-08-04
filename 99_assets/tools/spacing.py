# -*- coding: utf-8 -*-
"""図版と本文が混在するページの余白ルール。

素のデザインシステムは文章主体の想定で、.figure に margin-bottom が無いなど、
図版を挟むページでは詰まって見える箇所がある。ここで一括して整える。
"""

SPACING_CSS = """
/* ---- 余白（図版を挟む読み物向けに調整） ---- */
:root{--sec-pad:6rem 1.5rem}
.inner{max-width:960px}
.sec-title{margin-bottom:.9rem}
.sec-sub{margin-bottom:2.2rem;line-height:1.85}
.lede{margin:.2rem 0 2.2rem}
/* .figure は margin-bottom を持たないため、直後の要素と必ず詰まる */
.figure{margin:2.6rem 0 0;padding:2rem 1.8rem 1.6rem}
.figure + .cards,.figure + .stepper,.figure + .two-col,.figure + .note,
.figure + .role-block,.figure + .figure,.figure + .bare{margin-top:2.8rem}
.cards + .note,.stepper + .note,.two-col + .note,.cards + .figure{margin-top:2.2rem}
.note + .cards,.note + .stepper{margin-top:2rem}
.fig-title{margin-bottom:1.3rem;padding-bottom:.7rem}
.figure-cap{margin-top:1.4rem}
/* カードは本文が長いので、内側も外側も広げる */
.cards{gap:1.6rem}
.card{padding:1.7rem 1.8rem 1.6rem}
.card h3{margin-bottom:.6rem;line-height:1.6}
.card p{line-height:1.95}
.kicker{margin-bottom:0;padding-left:1.3rem}
@media(max-width:640px){
  :root{--sec-pad:4rem 1.2rem}
  .figure{padding:1.4rem 1.1rem 1.2rem}
  .card{padding:1.4rem 1.4rem 1.3rem}
}
"""


import re

_DIV = re.compile(r'<div\b|</div>')


def annotate_cards(html):
    """各 .cards に data-n（枚数）を付ける。

    4枚のカードが3列グリッドに入ると 3+1 になって最後の1枚が浮くため、
    枚数に応じて列数を決められるようにしておく。
    """
    out, i = [], 0
    while True:
        j = html.find('<div class="cards"', i)
        if j < 0:
            out.append(html[i:])
            return ''.join(out)
        gt = html.index('>', j)
        depth, p, n = 0, j, 0
        while True:
            m = _DIV.search(html, p)
            if not m:
                break
            if m.group(0) == '</div>':
                depth -= 1
                p = m.end()
                if depth == 0:
                    break
            else:
                depth += 1
                if depth == 2 and html.startswith('<div class="card">', m.start()):
                    n += 1
                p = m.end()
        out.append(html[i:gt])
        out.append(' data-n="%d">' % n)
        i = gt + 1


CARD_COLS_CSS = """
/* 4枚を3列に入れると最後の1枚が浮くので、枚数で列数を決める */
@media(min-width:760px){
  .cards[data-n="2"],.cards[data-n="4"]{grid-template-columns:repeat(2,1fr)}
  .cards[data-n="3"],.cards[data-n="5"],.cards[data-n="6"]{grid-template-columns:repeat(3,1fr)}
}
"""
