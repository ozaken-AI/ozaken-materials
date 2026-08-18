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
/* 配布物のダウンロード。CTAボタンではなく「資料に挟まれた配り物」として置く */
.dl{display:flex;flex-wrap:wrap;align-items:center;gap:1.1rem;
  margin:2.2rem 0 0;padding:1.4rem 1.5rem;border-radius:16px;
  border:1px solid var(--azure-pale);background:rgba(46,84,150,.05)}
.sec-navy .dl{border-color:rgba(255,255,255,.2);background:rgba(255,255,255,.06)}
.dl-body{flex:1 1 300px}
.dl-tag{display:inline-block;font-family:var(--font-en);font-size:.6rem;font-weight:700;
  letter-spacing:.16em;color:var(--navy-deep);background:var(--azure-pale);
  padding:3px 9px;border-radius:999px;margin-bottom:.5rem}
.dl h3{font-family:var(--font-ja-serif);font-size:1.08rem;font-weight:600;
  color:var(--ink);margin-bottom:.25rem}
.sec-navy .dl h3{color:#fff}
.dl p{font-size:.82rem;line-height:1.85;color:var(--muted)}
.sec-navy .dl p{color:rgba(255,255,255,.72)}
.dl-go{flex:none;font-family:var(--font-ja-sans);font-size:.86rem;font-weight:700;
  text-decoration:none;color:var(--azure);border:1px solid var(--azure);
  border-radius:999px;padding:.72em 1.5em;transition:background .2s ease,color .2s ease}
.dl-go:hover{background:var(--azure);color:#fff}
.sec-navy .dl-go{color:var(--azure-pale);border-color:var(--azure-pale)}
.sec-navy .dl-go:hover{background:var(--azure-pale);color:var(--navy-deep)}
@media print{.dl-go{display:none}}
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


def dl(href, title, note, label='PDFをダウンロード', tag='FREE DOWNLOAD'):
    """配布物のダウンロード。書き込むワークシートのように、
    資料を見ながら手を動かすものを渡すときに置く。

    **リンク先は暗号の外に置かれる。** 資料そのものは鍵で守られるが、
    ここに置くPDFは公開URLで誰でも取れる。パスワードを刷り込んだ紙は置かない。
    """
    return ('<div class="dl">\n  <div class="dl-body">\n'
            '    <span class="dl-tag">%s</span>\n'
            '    <h3>%s</h3>\n    <p>%s</p>\n  </div>\n'
            '  <a class="dl-go" href="%s" download>%s</a>\n</div>\n'
            % (tag, esc(title), note, href, esc(label)))


def cards(items, raw_head=True):
    """items: [(見出し, 本文)]。見出しに <span class="mth"> を入れたいときが多いので、
    既定では見出しをエスケープしない。素の文字列を入れたいときは raw_head=False"""
    return '\n'.join(
        '      <div class="card"><span class="card-tag">%02d</span><h3>%s</h3><p>%s</p></div>'
        % (i + 1, h if raw_head else esc(h), p) for i, (h, p) in enumerate(items))


def take(text, name='小澤健祐（おざけん）'):
    """おざけんのワンポイント。

    **毎回このHTMLを手で書いていたので、事故が繰り返された。**
    body（カードの格子）に混ぜてしまい、1列ぶんの幅に潰れる。
    sec(..., after=take('…')) の形で、カードの外に置く。

    アイコンは実物の顔写真を使う。頭文字の丸だと、
    誰の一言なのかが投影中に伝わらない。
    """
    return ('    <div class="take">\n'
            '      <img class="take-avatar" src="../99_assets/ozaken-avatar.jpg" '
            'alt="%s" loading="lazy">\n'
            '      <div class="take-body">\n'
            '        <div class="take-label">Ozaken\'s One Point</div>\n'
            '        <div class="take-author">%s</div>\n'
            '        <p class="take-text">%s</p>\n'
            '      </div>\n    </div>\n' % (name, name, text))


def sec(tone, eyebrow, title, sub=None, lede=None, fig=None, body=None, cattr='',
        after=None):
    """tone: 'sec-light' か 'sec-navy'。fig は必ず1つ以上入れる。

    **after はカードの外に置く。** ここを用意していなかったので、
    「おざけんのワンポイント」や注記を body に混ぜてしまい、
    カードの格子の中に入って1列ぶんの幅に潰れていた（実際に出た）。
    """
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
    if after:
        out.append(after)
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


def replace_figure(html, fig_no, new_html):
    """既存の図版を差し替える。fig_no は 'Fig.3' のような見出しの先頭。

    `<div class="figure">` から `</div>` までを正規表現で取ろうとすると、
    中の `<div class="figure-scroll">` を数え損ねて、
    **後ろにあるカードまで巻き込んで消す**。実際に2本の資料でカードが消えた。
    開きタグと閉じタグを数えて、対応する `</div>` を見つける。
    """
    import re
    m = re.search(r'<div class="figure">\s*<p class="fig-title">%s' % re.escape(fig_no), html)
    if not m:
        raise ValueError('%s が見つかりません' % fig_no)
    i = m.start()
    depth, j = 0, i
    for tag in re.finditer(r'<div\b|</div>', html[i:]):
        depth += 1 if tag.group(0).startswith('<div') else -1
        if depth == 0:
            j = i + tag.end()
            break
    else:
        raise ValueError('%s の閉じタグが見つかりません' % fig_no)
    return html[:i] + new_html + html[j:]
