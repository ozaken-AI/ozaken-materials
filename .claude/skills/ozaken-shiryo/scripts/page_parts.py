#!/usr/bin/env python3
"""本文フラグメントを組み立てる部品。

資料の骨組み（表紙・セクション・カード・締め）はどの資料でも同じ形なので、
ここに置いて使い回す。以前はこの部品が作業用の一時ディレクトリにあり、
セッションが変わると失われて、資料ごとに書き直す羽目になっていた。

  from page_parts import hero, sec, cards, close, EXTRA_CSS

図版は domain_fig の fig_* が返すHTMLを、そのまま sec(fig=...) に渡す。
複数枚を重ねたいときは '+' で連結する。
"""
from domain_fig import esc

# セクション共通の追加CSS。publish.py の --extra-css に渡す
EXTRA_CSS = """
.lede{font-family:var(--font-ja-serif);font-size:clamp(1.15rem,2.6vw,1.5rem);
  line-height:1.9;margin:.4rem 0 1.6rem}
.sec-navy .lede{color:rgba(255,255,255,.95)}
.cards[data-two]{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.mth{display:inline-block;font-family:var(--font-en);font-size:.62rem;font-weight:700;
  letter-spacing:.14em;color:var(--azure);background:var(--azure-pale);
  padding:2px 8px;border-radius:4px;margin-right:.5em;vertical-align:middle}
.sec-navy .mth{color:#fff;background:rgba(255,255,255,.18)}
.num{font-family:var(--font-en);font-weight:700;font-size:1.06em;letter-spacing:.02em}
"""

# 表紙の奥に薄く敷く格子と星座。地の色そのものは apply_herofx が当てる
HERO_TEXTURE = """  <div class="texture" aria-hidden="true">
    <svg viewBox="0 0 1200 600" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
      <defs><pattern id="pgr" width="46" height="46" patternUnits="userSpaceOnUse"><path d="M46 0H0V46" fill="none" stroke="#fff" stroke-width="0.7"/></pattern></defs>
      <rect width="1200" height="600" fill="url(#pgr)"/>
      <circle cx="240" cy="180" r="4" fill="#fff"/><circle cx="560" cy="350" r="4" fill="#fff"/><circle cx="880" cy="210" r="4" fill="#fff"/><circle cx="1040" cy="430" r="4" fill="#fff"/>
      <path d="M240 180L560 350L880 210L1040 430" stroke="#fff" stroke-width="1" fill="none"/>
    </svg>
  </div>
"""


def cards(items, raw_head=True):
    """items: [(見出し, 本文)]。見出しに <span class="mth"> を入れたいときが多いので、
    既定では見出しをエスケープしない。素の文字列を入れたいときは raw_head=False"""
    return '\n'.join(
        '      <div class="card"><span class="card-tag">%02d</span><h3>%s</h3><p>%s</p></div>'
        % (i + 1, h if raw_head else esc(h), p) for i, (h, p) in enumerate(items))


def sec(tone, eyebrow, title, sub=None, lede=None, fig=None, body=None, cattr=''):
    """tone: 'sec-light' か 'sec-navy'。fig は必ず1つ以上入れる"""
    out = ['<section class="%s">' % tone, '  <div class="inner" data-reveal>',
           '    <span class="eyebrow">%s</span>' % eyebrow,
           '    <h2 class="sec-title">%s</h2>' % title]
    if sub:
        out.append('    <p class="sec-sub">%s</p>' % sub)
    if lede:
        out.append('    <p class="lede">%s</p>' % lede)
    if fig:
        out.append(fig)
    if body:
        out.append('    <div class="cards"%s>' % cattr)
        out.append(body)
        out.append('    </div>')
    out += ['  </div>', '</section>', '']
    return '\n'.join(out)


def hero(eyebrow, title, copy):
    """title は <br> で2行に割る。「」の中か英字のかたまりが自動で赤くなる"""
    return ('<section class="hero">\n%s  <div class="inner" data-reveal>\n'
            '    <span class="eyebrow">%s</span>\n'
            '    <h1 class="hero-title">%s</h1>\n'
            '    <p class="hero-copy">%s</p>\n  </div>\n</section>\n'
            % (HERO_TEXTURE, eyebrow, title, esc(copy)))


def close(title, copy):
    """締め。図版は置かない。事実の要約ではなく、1段上から言い直す"""
    return ('<section class="sec-navy">\n  <div class="inner" data-reveal>\n'
            '    <span class="eyebrow">Summary</span>\n'
            '    <h2 class="sec-title">%s</h2>\n'
            '    <p class="kicker">%s</p>\n  </div>\n</section>\n' % (title, copy))
