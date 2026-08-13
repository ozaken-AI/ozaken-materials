#!/usr/bin/env python3
"""業界別・職種別資料で使うSVG図版のビルダー。

SVGのtextは折り返さないため、ラベルは短く保ち、必要な場合だけ
wrap() で明示的に行を分ける。色はデザインシステムのトークンに揃える。
"""

INK = '#1a1a2e'
NAVY = '#1f3864'
NAVY_DEEP = '#141d35'
AZURE = '#2e5496'
PALE = '#d8e4f0'
WHITE = '#ffffff'
RED = '#e23744'
MUTED = '#6b7a99'


def esc(t):
    return (t.replace('&', '&amp;').replace('<', '&lt;')
             .replace('>', '&gt;').replace('"', '&quot;'))


def _isw(c):
    """英数字の連なり（製品名・金額など）は途中で切りたくない"""
    return c.isascii() and (c.isalnum() or c in '.,$%-/')


def wrap(text, n):
    """n文字ごとに折り返す。ただし英数字の途中では切らない"""
    out, i, L = [], 0, len(text)
    while i < L:
        j = min(i + n, L)
        if j < L and _isw(text[j - 1]) and _isw(text[j]):
            k = j
            while k > i + 1 and _isw(text[k - 1]):
                k -= 1
            if k > i + max(2, n // 3):     # 行が極端に短くならない範囲で戻す
                j = k
        out.append(text[i:j])
        i = j
    return out or ['']


def _cw(c):
    """おおよその表示幅。全角は半角の2倍として数える"""
    return 2 if ord(c) > 0x2E7F else 1


def wrapw(text, cols):
    """**表示幅で折り返す。全角を2、半角を1として数える。**

    wrap() は文字数で数えるので、和文と欧文が混じる欄では
    どちらかが必ずはみ出す。たとえば幅21で折る欄に
    「Microsoft 365 Copilot」（21字＝幅21）を入れると収まるのに、
    「応募受付から書類整理・日程調整まで流す」（18字＝幅36）は溢れる。
    製品名と実例のように、和文と欧文のどちらも来る欄はこちらを使う。
    """
    out, cur, w = [], [], 0
    for i, ch in enumerate(text):
        cw = _cw(ch)
        if w + cw > cols and cur:
            # 英数字の連なりの途中では切らない。wrap() と同じ扱い
            if _isw(cur[-1]) and _isw(ch):
                k = len(cur)
                while k > 1 and _isw(cur[k - 1]):
                    k -= 1
                if k > 1:
                    out.append(''.join(cur[:k]))
                    cur = cur[k:]
                    w = sum(_cw(c) for c in cur)
                    cur.append(ch)
                    w += cw
                    continue
            out.append(''.join(cur))
            cur, w = [], 0
        cur.append(ch)
        w += cw
    if cur:
        out.append(''.join(cur))
    return out or ['']


def lines(text, x, y, n, lh, **kw):
    """折り返した複数行のtspanを持つtext要素"""
    attrs = ' '.join('%s="%s"' % (k.replace('_', '-'), v) for k, v in kw.items())
    ls = wrap(text, n)
    ts = ''.join('<tspan x="%s" dy="%s">%s</tspan>'
                 % (x, 0 if i == 0 else lh, esc(l)) for i, l in enumerate(ls))
    return '<text x="%s" y="%s" %s>%s</text>' % (x, y, attrs, ts)


import re as _re

# 図版に動きを与える。スタイル側に a-fade / a-pop / a-grow / a-draw の仕掛けが
# すでにあるので、ここでは要素に印と遅延を振るだけでよい。
# 描画順に少しずつ遅らせると、図が組み上がっていくように見える。
_TAG = _re.compile(r'<(rect|circle|line|path|text|ellipse|polygon|polyline)([^>]*)>')


def _animate(svg, window=1.05):
    """SVGの各要素に、描画順の遅延つきで a-fade を振る。
    すでに a-grow などが個別に付いている要素は、その指定を尊重して遅延だけ足す。"""
    # defs の中（marker や pattern の定義）は動かさないので、いったん退避する
    defs = []

    def stash(m):
        defs.append(m.group(0))
        return '\x00%d\x00' % (len(defs) - 1)

    body = _re.sub(r'<defs>[\s\S]*?</defs>', stash, svg)
    n = len(_TAG.findall(body)) or 1
    step = min(0.045, window / n)
    idx = [0]

    def rewrite(m):
        tag, attrs = m.group(1), m.group(2)
        close = ''
        if attrs.rstrip().endswith('/'):        # 自己終了タグの / は末尾へ戻す
            attrs = attrs.rstrip()[:-1]
            close = '/'
        d = '%.3fs' % (idx[0] * step)
        idx[0] += 1
        if '--d' in attrs:
            return m.group(0)
        # 出たあとも動き続けるものを、形から判断して振り分ける。
        # 投影中に気が散らないよう、動きはどれもゆっくり・小さくしてある
        if 'class="a-' not in attrs:
            r = _re.search(r'\br="([\d.]+)"', attrs)
            hollow = 'fill="none"' in attrs or 'fill:none' in attrs
            if 'marker-end' in attrs or 'stroke-dasharray' in attrs:
                attrs += ' class="a-flow"'          # 矢印・破線は流れ続ける
            elif tag == 'circle' and r and not hollow:
                # 大きめの丸（VSの座や見出しの座）はゆっくり脈打つ。
                # 小さな点は動かすと落ち着かないので、明るさだけ揺らす
                attrs += ' class="a-pulse"' if float(r.group(1)) >= 13 else ' class="a-breathe"'
            elif tag == 'rect' and _re.search(r'height="([2-6])"', attrs) and 'rx=' in attrs:
                attrs += ' class="a-breathe"'       # カード上端の細い色帯は呼吸する
        if 'class="a-' in attrs:               # 個別に指定済み。遅延だけ足す
            if 'style="' in attrs:
                attrs = attrs.replace('style="', 'style="--d:%s;' % d, 1)
            else:
                attrs += ' style="--d:%s"' % d
        else:
            # class や style がすでにあるなら、そこに混ぜる。属性を二重に書かない
            if 'class="' in attrs:
                attrs = attrs.replace('class="', 'class="a-fade ', 1)
            else:
                attrs += ' class="a-fade"'
            if 'style="' in attrs:
                attrs = attrs.replace('style="', 'style="--d:%s;' % d, 1)
            else:
                attrs += ' style="--d:%s"' % d
        return '<%s%s%s>' % (tag, attrs, close)

    body = _TAG.sub(rewrite, body)
    return _re.sub(r'\x00(\d+)\x00', lambda m: defs[int(m.group(1))], body)


def _fig(title, cap, svg, anim=True):
    if anim:
        svg = _animate(svg)
    return ('<div class="figure">\n  <p class="fig-title">%s</p>\n'
            '  <div class="figure-scroll">%s</div>\n'
            '  <p class="figure-cap">%s</p>\n</div>' % (esc(title), svg, esc(cap)))


# ------------------------------------------------------------------
# F1  いま → 3年後 のギャップ
# ------------------------------------------------------------------
def fig_gap(pairs, title, cap, dark=False, uid='',
            left_label='いま', right_label='3年後の到達像'):
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.62)' if dark else MUTED
    lbox = 'rgba(255,255,255,.06)' if dark else '#eef1f6'
    rbox = 'rgba(46,84,150,.35)' if dark else PALE
    stroke = 'rgba(255,255,255,.18)' if dark else 'rgba(46,84,150,.25)'
    h = 108 + len(pairs) * 76
    rows = []
    for i, (a, b) in enumerate(pairs):
        y = 104 + i * 76
        rows.append(
            '<rect x="16" y="%d" width="368" height="60" rx="8" fill="%s"/>'
            '<rect x="516" y="%d" width="368" height="60" rx="8" fill="%s"/>'
            % (y, lbox, y, rbox))
        rows.append(lines(a, 34, y + 26, 22, 21, fill=sub, font_size='14'))
        rows.append(lines(b, 534, y + 26, 22, 21, fill=fg, font_size='14',
                          font_weight='600'))
        rows.append('<path d="M410 %d L490 %d" stroke="%s" stroke-width="2" '
                    'fill="none" marker-end="url(#gaparrow%s)"/>' % (y + 30, y + 30, AZURE, uid))
    return _fig(title, cap,
        '<svg viewBox="0 0 900 %d" xmlns="http://www.w3.org/2000/svg" role="img">'
        '<defs><marker id="gaparrow%s" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M0 0L10 5L0 10z" fill="%s"/></marker></defs>'
        '<text x="16" y="34" fill="%s" font-size="13" font-weight="700" '
        'letter-spacing="1.5">%s</text>'
        '<text x="516" y="34" fill="%s" font-size="13" font-weight="700" '
        'letter-spacing="1.5">%s</text>'
        '<line x1="16" y1="52" x2="384" y2="52" stroke="%s" stroke-width="1"/>'
        '<line x1="516" y1="52" x2="884" y2="52" stroke="%s" stroke-width="1"/>'
        '%s</svg>' % (h, uid, AZURE, sub, esc(left_label),
                      AZURE if not dark else PALE, esc(right_label),
                      stroke, stroke, ''.join(rows)))


# ------------------------------------------------------------------
# F2  課題の連鎖（4つの壁）
# ------------------------------------------------------------------
def fig_issues(items, title, cap, dark=False, uid=''):
    """items: [(短ラベル, ひとこと)] を横に並べ、連なっていることを示す"""
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.6)' if dark else MUTED
    box = 'rgba(255,255,255,.06)' if dark else WHITE
    edge = 'rgba(255,255,255,.16)' if dark else 'rgba(46,84,150,.22)'
    n = len(items)
    w = int((884 - 16 - (n - 1) * 34) / n)
    parts = []
    for i, (lab, note) in enumerate(items):
        x = 16 + i * (w + 34)
        parts.append(
            '<rect x="%d" y="40" width="%d" height="150" rx="10" fill="%s" '
            'stroke="%s" stroke-width="1"/>' % (x, w, box, edge))
        parts.append('<rect x="%d" y="40" width="%d" height="4" rx="2" fill="%s"/>'
                     % (x, w, RED))
        parts.append('<text x="%d" y="76" fill="%s" font-size="12" '
                     'font-weight="700" letter-spacing="1.2">壁 %d</text>'
                     % (x + 18, RED, i + 1))
        parts.append(lines(lab, x + 18, 102, 9, 22, fill=fg, font_size='15',
                           font_weight='700'))
        parts.append(lines(note, x + 18, 152, 11, 18, fill=sub, font_size='12'))
        if i < n - 1:
            cx = x + w + 6
            parts.append('<path d="M%d 115 L%d 115" stroke="%s" stroke-width="2" '
                         'fill="none" marker-end="url(#isarrow%s)"/>' % (cx, cx + 22, AZURE, uid))
    return _fig(title, cap,
        '<svg viewBox="0 0 900 210" xmlns="http://www.w3.org/2000/svg" role="img">'
        '<defs><marker id="isarrow%s" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M0 0L10 5L0 10z" fill="%s"/></marker></defs>%s</svg>'
        % (uid, AZURE, ''.join(parts)))


# ------------------------------------------------------------------
# F3  コンテキストの4層
# ------------------------------------------------------------------
def fig_context(layers, title, cap, dark=False):
    """layers: [(層名, 具体例)] を下から積み上げた台形状の帯で示す"""
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.6)' if dark else MUTED
    n = len(layers)
    parts = []
    for i, (name, ex) in enumerate(layers):
        y = 30 + i * 74
        w = 520 - i * 76
        x = 16
        op = 0.9 - i * 0.16
        parts.append('<rect x="%d" y="%d" width="%d" height="58" rx="8" '
                     'fill="%s" fill-opacity="%.2f"/>' % (x, y, w, AZURE, op))
        parts.append('<text x="%d" y="%d" fill="%s" font-size="14" '
                     'font-weight="700">%s</text>' % (x + 20, y + 34, WHITE, esc(name)))
        parts.append('<text x="560" y="%d" fill="%s" font-size="12" '
                     'font-weight="700">L%d</text>' % (y + 26, AZURE if not dark else PALE, i + 1))
        parts.append(lines(ex, 600, y + 26, 24, 18, fill=sub, font_size='12'))
        if i < n - 1:
            parts.append('<line x1="%d" y1="%d" x2="884" y2="%d" stroke="%s" '
                         'stroke-width="1" stroke-dasharray="3 4"/>'
                         % (x, y + 66, y + 66,
                            'rgba(255,255,255,.14)' if dark else 'rgba(46,84,150,.18)'))
    h = 30 + n * 74 + 16
    parts.append('<text x="16" y="%d" fill="%s" font-size="12">'
                 '下の層ほど整備しやすく、上の層ほど成果に効く</text>'
                 % (h - 4, sub))
    return _fig(title, cap,
        '<svg viewBox="0 0 900 %d" xmlns="http://www.w3.org/2000/svg" role="img">'
        '%s</svg>' % (h + 8, ''.join(parts)))


# ------------------------------------------------------------------
# F4  3類型のレーン（決める → 組む → 回す）
# ------------------------------------------------------------------
ROLES = [('ストラテジスト', 'どこに置くかを決める', 'STRATEGIST'),
         ('アーキテクト', 'どう組むかを設計する', 'ARCHITECT'),
         ('オペレーター', '日々の業務で回す', 'OPERATOR')]


def fig_roles(who, title, cap, dark=False):
    """who: [ストラテジストの担当, アーキテクトの担当, オペレーターの担当]"""
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.62)' if dark else MUTED
    box = 'rgba(255,255,255,.06)' if dark else WHITE
    edge = 'rgba(255,255,255,.16)' if dark else 'rgba(46,84,150,.22)'
    parts = []
    for i, ((ja, verb, en), duty) in enumerate(zip(ROLES, who)):
        x = 16 + i * 296
        parts.append('<rect x="%d" y="34" width="272" height="188" rx="10" '
                     'fill="%s" stroke="%s" stroke-width="1"/>' % (x, box, edge))
        parts.append('<rect x="%d" y="34" width="272" height="4" rx="2" fill="%s"/>'
                     % (x, AZURE))
        parts.append('<text x="%d" y="66" fill="%s" font-size="11" '
                     'font-weight="700" letter-spacing="1.4">%s</text>'
                     % (x + 20, AZURE if not dark else PALE, en))
        parts.append('<text x="%d" y="94" fill="%s" font-size="16" '
                     'font-weight="700">%s</text>' % (x + 20, fg, esc(ja)))
        parts.append('<text x="%d" y="118" fill="%s" font-size="12">%s</text>'
                     % (x + 20, sub, esc(verb)))
        parts.append('<line x1="%d" y1="132" x2="%d" y2="132" stroke="%s" '
                     'stroke-width="1" stroke-dasharray="3 4"/>'
                     % (x + 20, x + 268, edge))
        parts.append(lines(duty, x + 20, 156, 15, 21, fill=fg, font_size='13'))
        if i < 2:
            parts.append('<path d="M%d 128 L%d 128" stroke="%s" stroke-width="2" '
                         'fill="none" marker-end="url(#rlarrow)"/>'
                         % (x + 274, x + 292, AZURE))
    return _fig(title, cap,
        '<svg viewBox="0 0 900 236" xmlns="http://www.w3.org/2000/svg" role="img">'
        '<defs><marker id="rlarrow" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M0 0L10 5L0 10z" fill="%s"/></marker></defs>%s</svg>'
        % (AZURE, ''.join(parts)))


# ------------------------------------------------------------------
# F5  KPIツリー
# ------------------------------------------------------------------
def fig_kpi(top, branches, title, cap, dark=False):
    """branches: [(中位指標, [下位指標, ...])] 最大3本"""
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.62)' if dark else MUTED
    box = 'rgba(255,255,255,.06)' if dark else WHITE
    edge = 'rgba(255,255,255,.16)' if dark else 'rgba(46,84,150,.22)'
    parts = ['<rect x="270" y="16" width="360" height="60" rx="10" fill="%s"/>'
             % (AZURE if not dark else 'rgba(46,84,150,.6)')]
    parts.append(lines(top, 450, 44, 26, 20, fill=WHITE, font_size='15',
                       font_weight='700', text_anchor='middle'))
    n = len(branches)
    w = int((884 - 16 - (n - 1) * 28) / n)
    maxleaf = max(len(ls) for _, ls in branches)
    h = 190 + maxleaf * 34
    for i, (mid, leaves) in enumerate(branches):
        x = 16 + i * (w + 28)
        cx = x + w / 2
        parts.append('<path d="M450 76 L450 100 L%d 100 L%d 122" stroke="%s" '
                     'stroke-width="1.5" fill="none"/>' % (cx, cx, edge))
        parts.append('<rect x="%d" y="122" width="%d" height="52" rx="8" fill="%s" '
                     'stroke="%s" stroke-width="1"/>' % (x, w, box, edge))
        parts.append(lines(mid, cx, 146, 14, 18, fill=fg, font_size='13',
                           font_weight='700', text_anchor='middle'))
        for j, lf in enumerate(leaves):
            y = 200 + j * 34
            parts.append('<circle cx="%d" cy="%d" r="3" fill="%s"/>'
                         % (x + 12, y - 5, AZURE if not dark else PALE))
            parts.append('<line x1="%d" y1="174" x2="%d" y2="%d" stroke="%s" '
                         'stroke-width="1" fill="none"/>' % (x + 12, x + 12, y - 8, edge))
            parts.append(lines(lf, x + 24, y, 18, 16, fill=sub, font_size='12'))
    return _fig(title, cap,
        '<svg viewBox="0 0 900 %d" xmlns="http://www.w3.org/2000/svg" role="img">'
        '%s</svg>' % (h, ''.join(parts)))


# ------------------------------------------------------------------
# F6  2×2マトリクス（区分の整理に使う）
# ------------------------------------------------------------------
def fig_quad(xlab, ylab, cells, title, cap, dark=False, xpoles=None, ypoles=None):
    """cells: [(見出し, 補足, 危険度0-2)] を左上→右上→左下→右下の順で4つ

    **xpoles / ypoles を渡すと、軸の両端が何を指すかが出る。**
    軸名だけだと「言語化されているか」と書いてあっても、
    右がイエスなのか左がイエスなのかが読み手に分からない。
    実際「左右と上下が分かりにくい」と何度も言われた欄。

      xpoles=('まだ言葉になっていない', '言葉になっている')   左 → 右
      ypoles=('外から与えられた', '自分の内側から出ている')     下 → 上

    省略すると軸名だけの従来の形になるので、既存の呼び出しはそのまま動く。
    """
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.6)' if dark else MUTED
    pol = 'rgba(255,255,255,.82)' if dark else INK
    edge = 'rgba(255,255,255,.16)' if dark else 'rgba(46,84,150,.22)'
    tone = [('rgba(46,84,150,.16)', AZURE), ('rgba(226,55,68,.12)', '#c9762f'),
            ('rgba(226,55,68,.18)', RED)]
    TOP = 76 if xpoles else 56          # 両端を出すぶん、盤面を1段下げる
    H = TOP + 340
    parts = []
    for i, (h, note, lv) in enumerate(cells):
        cx = 120 + (i % 2) * 372
        cy = TOP + (i // 2) * 168
        bg, bar = tone[lv]
        parts.append('<rect x="%d" y="%d" width="356" height="152" rx="10" '
                     'fill="%s" stroke="%s" stroke-width="1"/>' % (cx, cy, bg, edge))
        parts.append('<rect x="%d" y="%d" width="356" height="4" rx="2" fill="%s"/>'
                     % (cx, cy, bar))
        parts.append(lines(h, cx + 20, cy + 40, 17, 24, fill=fg, font_size='15',
                           font_weight='700'))
        parts.append(lines(note, cx + 20, cy + 90, 21, 19, fill=sub, font_size='12'))
    parts.append('<text x="470" y="%d" fill="%s" font-size="12" font-weight="700" '
                 'text-anchor="middle">%s</text>' % (20 if xpoles else 24, sub, esc(xlab)))
    if xpoles:
        # 左端と右端に、その側が何を指すかを置く。矢印はここでは横書きなので使える
        parts.append('<text x="120" y="46" fill="%s" font-size="12" font-weight="700">'
                     '← %s</text>' % (pol, esc(xpoles[0])))
        parts.append('<text x="848" y="46" fill="%s" font-size="12" font-weight="700" '
                     'text-anchor="end">%s →</text>' % (pol, esc(xpoles[1])))
    # 回転テキストに矢印グリフを入れると向きが破綻するため、必ず落とす
    def _ysafe(t):
        return ''.join(c for c in t if c not in '↑↓←→')
    parts.append('<text x="0" y="0" fill="%s" font-size="12" font-weight="700" '
                 'text-anchor="middle" transform="translate(%d %d) rotate(-90)">%s</text>'
                 % (sub, 26 if ypoles else 28, TOP + 170, esc(_ysafe(ylab))))
    if ypoles:
        # 縦は回転させて、下端＝下の意味／上端＝上の意味。読みは下から上へ。
        # **rotate(-90) では字が下から上へ進む。** だから下の札は始点を下端に置き、
        # 上の札は終点を上端に置く。逆にすると、どちらも枠の外へ出て頭が切れる
        parts.append('<text x="0" y="0" fill="%s" font-size="12" font-weight="700" '
                     'transform="translate(50 %d) rotate(-90)">%s</text>'
                     % (pol, H - 22, esc(_ysafe(ypoles[0]))))
        parts.append('<text x="0" y="0" fill="%s" font-size="12" font-weight="700" '
                     'text-anchor="end" transform="translate(50 %d) rotate(-90)">%s</text>'
                     % (pol, TOP + 6, esc(_ysafe(ypoles[1]))))
    parts.append('<path d="M96 %d L96 %d" stroke="%s" stroke-width="1" fill="none"/>'
                 % (H - 16, TOP - 16, edge))
    parts.append('<path d="M96 %d L884 %d" stroke="%s" stroke-width="1" fill="none"/>'
                 % (H - 16, H - 16, edge))
    return _fig(title, cap,
        '<svg viewBox="0 0 900 %d" xmlns="http://www.w3.org/2000/svg" role="img">'
        '%s</svg>' % (H, ''.join(parts)))


# ------------------------------------------------------------------
# F7  段（層を上に積む。手順にも、抽象度の階段にも使う）
# ------------------------------------------------------------------
def fig_ladder(items, title, cap, dark=False, asc=True):
    """items: [(見出し, 補足)] を下から上へ／上から下へ並べる"""
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.6)' if dark else MUTED
    box = 'rgba(255,255,255,.06)' if dark else WHITE
    edge = 'rgba(255,255,255,.16)' if dark else 'rgba(46,84,150,.22)'
    n = len(items)
    parts = []
    for i, (h, note) in enumerate(items):
        y = 20 + i * 84
        ind = (n - 1 - i) * 40 if asc else i * 40
        x = 16 + ind
        parts.append('<rect x="%d" y="%d" width="%d" height="68" rx="10" fill="%s" '
                     'stroke="%s" stroke-width="1"/>' % (x, y, 884 - x, box, edge))
        parts.append('<rect x="%d" y="%d" width="4" height="68" rx="2" fill="%s" '
                     'fill-opacity="%.2f"/>' % (x, y, AZURE, 1 - i * 0.15))
        parts.append('<text x="%d" y="%d" fill="%s" font-size="11" font-weight="700" '
                     'letter-spacing="1.2">%02d</text>'
                     % (x + 22, y + 26, AZURE if not dark else PALE, i + 1))
        parts.append('<text x="%d" y="%d" fill="%s" font-size="15" font-weight="700">%s</text>'
                     % (x + 58, y + 28, fg, esc(h)))
        parts.append(lines(note, x + 58, y + 52, 52, 18, fill=sub, font_size='12'))
    return _fig(title, cap,
        '<svg viewBox="0 0 900 %d" xmlns="http://www.w3.org/2000/svg" role="img">'
        '%s</svg>' % (20 + n * 84, ''.join(parts)))


# ------------------------------------------------------------------
# F8  ワークシート（記入例つきの表）
#     スタイルガイドで <table> を禁じているため、SVGで組む
# ------------------------------------------------------------------
def fig_sheet(headers, rows, widths, title, cap, dark=False, note=None,
              badge='記入例'):
    """headers: [列名]、rows: [[セル,...]]、widths: 合計1.0になる列幅の比"""
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.72)' if dark else MUTED
    grid = 'rgba(255,255,255,.14)' if dark else 'rgba(46,84,150,.18)'
    zebra = 'rgba(255,255,255,.035)' if dark else 'rgba(46,84,150,.035)'
    X0, W = 14, 872
    xs, acc = [], X0
    for w in widths:
        xs.append(acc)
        acc += W * w
    xs.append(X0 + W)

    def cap_chars(i):
        return max(4, int((xs[i + 1] - xs[i] - 16) / 11.2))

    parts = []
    y = 34
    # 見出し行
    parts.append('<rect x="%d" y="%d" width="%d" height="34" rx="6" fill="%s"/>'
                 % (X0, y, W, AZURE if not dark else 'rgba(46,84,150,.72)'))
    for i, h in enumerate(headers):
        parts.append('<text x="%.1f" y="%d" fill="%s" font-size="11.5" '
                     'font-weight="700">%s</text>' % (xs[i] + 10, y + 22, WHITE, esc(h)))
    y += 34
    for r, row in enumerate(rows):
        nl = max(len(wrap(str(c), cap_chars(i))) for i, c in enumerate(row))
        h = 20 + nl * 17
        if r % 2:
            parts.append('<rect x="%d" y="%.1f" width="%d" height="%.1f" fill="%s"/>'
                         % (X0, y, W, h, zebra))
        parts.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" '
                     'stroke-width="1"/>' % (X0, y, X0 + W, y, grid))
        for i, c in enumerate(row):
            col = fg if i == 0 else sub
            wt = '700' if i == 0 else '400'
            parts.append(lines(str(c), xs[i] + 10, y + 20, cap_chars(i), 17,
                               fill=col, font_size='11.5', font_weight=wt))
        y += h
    parts.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" '
                 'stroke-width="1"/>' % (X0, y, X0 + W, y, grid))
    for i in range(1, len(headers)):
        parts.append('<line x1="%.1f" y1="34" x2="%.1f" y2="%.1f" stroke="%s" '
                     'stroke-width="1"/>' % (xs[i], xs[i], y, grid))
    if badge:
        parts.append('<text x="%d" y="24" fill="%s" font-size="10.5" font-weight="700" '
                     'letter-spacing="2">%s</text>'
                     % (X0, AZURE if not dark else PALE, esc(badge)))
    if note:
        y += 22
        parts.append(lines(note, X0, y, 78, 17, fill=sub, font_size='11'))
        y += 8
    return _fig(title, cap,
        '<svg viewBox="0 0 900 %.0f" xmlns="http://www.w3.org/2000/svg" role="img">'
        '%s</svg>' % (y + 10, ''.join(parts)))


# ------------------------------------------------------------------
# F9  横棒グラフ（金額や比率の比較に使う）
# ------------------------------------------------------------------
def fig_bars(items, title, cap, dark=False, unit='', note=None):
    """items: [(ラベル, 数値, 表示値, 補足, 強調0/1/2)]"""
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.6)' if dark else MUTED
    track = 'rgba(255,255,255,.07)' if dark else 'rgba(46,84,150,.08)'
    tone = [AZURE, '#c9762f', RED]
    mx = max(v for _, v, _, _, _ in items) or 1
    X, W = 250, 500
    parts = []
    y = 30
    for lab, v, disp, sup, lv in items:
        parts.append(lines(lab, 14, y + 20, 18, 18, fill=fg, font_size='13',
                           font_weight='700'))
        parts.append('<rect x="%d" y="%d" width="%d" height="26" rx="5" fill="%s"/>'
                     % (X, y + 4, W, track))
        w = max(6, W * v / mx)
        parts.append('<rect class="a-grow" x="%d" y="%d" width="%.1f" height="26" rx="5" '
                     'fill="%s" fill-opacity="%.2f"/>' % (X, y + 4, w, tone[lv], .9 if lv else .8))
        parts.append('<text x="%.1f" y="%d" fill="%s" font-size="13" '
                     'font-weight="700">%s</text>'
                     % (X + w + 12, y + 23, fg, esc(disp)))
        if sup:
            parts.append(lines(sup, 14, y + 40, 30, 16, fill=sub, font_size='11'))
            y += 62
        else:
            y += 46
    if note:
        parts.append(lines(note, 14, y + 14, 74, 17, fill=sub, font_size='11'))
        y += 26
    if unit:
        parts.append('<text x="%d" y="20" fill="%s" font-size="10.5" '
                     'font-weight="700" letter-spacing="1.6">%s</text>'
                     % (X, sub, esc(unit)))
    return _fig(title, cap,
        '<svg viewBox="0 0 900 %d" xmlns="http://www.w3.org/2000/svg" role="img">'
        '%s</svg>' % (y + 12, ''.join(parts)))


AMBER = '#c9762f'
TEAL = '#2f8f8a'
ACCENTS = [AZURE, RED, AMBER, TEAL]
# 紺地の上では AZURE が地に沈んで、番号も色帯もほとんど見えない。
# 琥珀と青緑は紺の上でも立つので、青と赤だけ明るいほうに寄せる
ACCENTS_ON_NAVY = ['#8fb0e0', '#ff5d6a', AMBER, TEAL]


def accents(dark):
    return ACCENTS_ON_NAVY if dark else ACCENTS


# ------------------------------------------------------------------
# F10  年表（時間の流れと、主体ごとの色分け）
# ------------------------------------------------------------------
def fig_timeline(events, title, cap, dark=False, axis='2026年5月'):
    """events: [(日付, 主体, 出来事, 意味, 差し色index)]"""
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.68)' if dark else MUTED
    box = 'rgba(255,255,255,.05)' if dark else WHITE
    edge = 'rgba(255,255,255,.14)' if dark else 'rgba(46,84,150,.18)'
    acc = accents(dark)
    n = len(events)
    w = int((884 - 16 - (n - 1) * 20) / n)
    LY = 66
    parts = ['<line x1="16" y1="%d" x2="884" y2="%d" stroke="%s" stroke-width="2"/>'
             % (LY, LY, edge)]
    parts.append('<text x="16" y="26" fill="%s" font-size="11" font-weight="700" '
                 'letter-spacing="2.4">%s</text>' % (sub, esc(axis)))
    for i, (date, who, what, mean, ai) in enumerate(events):
        x = 16 + i * (w + 20)
        c = acc[ai % len(acc)]
        cx = x + w / 2
        parts.append('<circle cx="%.1f" cy="%d" r="7" fill="%s"/>' % (cx, LY, c))
        parts.append('<circle cx="%.1f" cy="%d" r="13" fill="%s" fill-opacity=".18"/>'
                     % (cx, LY, c))
        parts.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="96" stroke="%s" '
                     'stroke-width="1.5"/>' % (cx, LY + 13, cx, c))
        parts.append(lines(date, cx, 44, 12, 14, fill=c, font_size='11.5',
                           font_weight='700', text_anchor='middle'))
        parts.append('<rect x="%d" y="96" width="%d" height="190" rx="10" fill="%s" '
                     'stroke="%s" stroke-width="1"/>' % (x, w, box, edge))
        parts.append('<rect x="%d" y="96" width="%d" height="4" rx="2" fill="%s"/>'
                     % (x, w, c))
        parts.append(lines(who, x + 16, 126, 13, 18, fill=c, font_size='13',
                           font_weight='700'))
        parts.append(lines(what, x + 16, 156, 15, 18, fill=fg, font_size='12'))
        parts.append('<line x1="%d" y1="228" x2="%d" y2="228" stroke="%s" '
                     'stroke-width="1" stroke-dasharray="3 4"/>' % (x + 16, x + w - 16, edge))
        parts.append(lines(mean, x + 16, 250, 15, 17, fill=sub, font_size='11.5'))
    return _fig(title, cap,
        '<svg viewBox="0 0 900 300" xmlns="http://www.w3.org/2000/svg" role="img">'
        '%s</svg>' % ''.join(parts))


# ------------------------------------------------------------------
# F11  ピラミッド（層の希少性・量の違いを面積で見せる）
# ------------------------------------------------------------------
def fig_pyramid(layers, title, cap, dark=False, left_label='', right_label=''):
    """layers: [(層名, 説明, 差し色index)] 上ほど希少・少量"""
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.66)' if dark else MUTED
    n = len(layers)
    CX, TOPW, BOTW, H = 300, 150, 470, 92
    parts = []
    for i, (name, desc, ai) in enumerate(layers):
        c = ACCENTS[ai % len(ACCENTS)]
        y = 24 + i * H
        wt = TOPW + (BOTW - TOPW) * i / max(1, n - 1)
        wb = TOPW + (BOTW - TOPW) * (i + 1) / max(1, n - 1)
        parts.append('<path d="M%.1f %d L%.1f %d L%.1f %d L%.1f %d Z" fill="%s" '
                     'fill-opacity="%.2f" stroke="%s" stroke-width="1.5"/>'
                     % (CX - wt / 2, y, CX + wt / 2, y, CX + wb / 2, y + H - 10,
                        CX - wb / 2, y + H - 10, c,
                        # 暗い面では薄い塗りが地に沈んで濁って見えるので、少し濃くする
                        (.34 if dark else .22) + i * .06, c))
        parts.append(lines(name, CX, y + H / 2 - 2, 12, 20, fill=fg, font_size='14',
                           font_weight='700', text_anchor='middle'))
        parts.append('<line x1="%.1f" y1="%.1f" x2="596" y2="%.1f" stroke="%s" '
                     'stroke-width="1" stroke-dasharray="3 4"/>'
                     % (CX + wb / 2, y + H / 2, y + H / 2, c))
        parts.append('<circle cx="600" cy="%.1f" r="4" fill="%s"/>' % (y + H / 2, c))
        parts.append(lines(desc, 616, y + H / 2 - 6, 21, 18, fill=sub, font_size='12'))
    h = 24 + n * H + 24
    if left_label:
        parts.append('<text x="0" y="0" fill="%s" font-size="11" font-weight="700" '
                     'letter-spacing="1.6" text-anchor="middle" '
                     'transform="translate(30 %d) rotate(-90)">%s</text>'
                     % (sub, 24 + n * H / 2, esc(left_label)))
    if right_label:
        parts.append('<text x="16" y="%d" fill="%s" font-size="11">%s</text>'
                     % (h - 6, sub, esc(right_label)))
    return _fig(title, cap,
        '<svg viewBox="0 0 900 %d" xmlns="http://www.w3.org/2000/svg" role="img">'
        '%s</svg>' % (h, ''.join(parts)))


# ------------------------------------------------------------------
# F12b  水位（下から順に沈んでいく3層）
# ------------------------------------------------------------------
def fig_waterline(layers, title, cap, dark=False, note=None,
                  water_at=1, water_label='AIの水位', rising='上昇中'):
    """layers: [(英字, 見出し, 説明, 右の見出し, 右の補足)] を上から3つ。

    **帯グラフでは「水面」が描けない。**
    fig_ranges は「どこまで伸びているか」は出せるが、
    水位が下から上がってくるという一方向の動きが出ない。
    ここでは層を積み、その中ほどに水面を引いて、下を水で満たす。

      water_at   何番目の層（0始まり）の中ほどに水面を置くか
      right      各層の右に置く注釈。水面のある層だけは水位の札に替わる
    """
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.62)' if dark else MUTED
    box = 'rgba(255,255,255,.10)' if dark else 'rgba(46,84,150,.05)'
    edge = PALE if dark else 'rgba(46,84,150,.3)'
    red = '#ff5d6a' if dark else RED
    wet = 'rgba(255,255,255,.78)' if dark else MUTED
    X, BW, BH, GY, Y0 = 40, 540, 88, 18, 24
    RX = 620                                   # 右の注釈を置く列
    H = Y0 + BH * 3 + GY * 2 + 26
    wy = Y0 + (BH + GY) * water_at + BH / 2    # 水面の高さ
    parts = []
    # **水は層より先に描く。** あとから描くと箱の文字が沈んで読めなくなる
    parts.append('<rect x="0" y="%.1f" width="900" height="%.1f" fill="%s" '
                 'fill-opacity="%s"/>' % (wy, H - wy, AZURE, '.5' if dark else '.14'))
    for i, (en, name, desc, rhead, rsub) in enumerate(layers):
        y = Y0 + (BH + GY) * i
        under = y > wy                          # 完全に水面下の層
        parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="8" fill="%s" '
                     'stroke="%s" stroke-width="1.5"/>' % (X, y, BW, BH, box, edge))
        parts.append('<text x="%d" y="%.1f" fill="%s" font-size="15" font-weight="700" '
                     'letter-spacing=".08em">%s</text>'
                     % (X + 22, y + 36, fg, esc(en)))
        parts.append('<text x="%d" y="%.1f" fill="%s" font-size="13.5" '
                     'font-weight="700">%s</text>'
                     % (X + 132, y + 36, fg, esc(name)))
        parts.append(lines(desc, X + 22, y + 62, 38, 16,
                           fill=wet if under else sub, font_size='11.5'))
        if i == water_at:
            parts.append('<text x="%d" y="%.1f" fill="%s" font-size="12.5" '
                         'font-weight="700">%s</text>' % (RX, wy - 8, red, esc(water_label)))
        if rhead:
            parts.append('<text x="%d" y="%.1f" fill="%s" font-size="12.5" '
                         'font-weight="700">%s</text>'
                         % (RX, y + 36, fg, esc(rhead)))
        if rsub:
            parts.append(lines(rsub, RX, y + 58, 17, 15,
                               fill=wet if under else sub, font_size='11'))
    # 水面の線。破線は _animate が流れる動きに振り分ける
    parts.append('<line x1="0" y1="%.1f" x2="900" y2="%.1f" stroke="%s" '
                 'stroke-width="2" stroke-dasharray="8 6"/>' % (wy, wy, red))
    # 上昇の矢印。水の中を下から突き上げる
    ax, atop = 856, wy + 34
    parts.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" '
                 'stroke-width="2"/>' % (ax, H - 40, ax, atop, red))
    parts.append('<path d="M%d %.1f l-7 12 h14 z" fill="%s"/>' % (ax, atop - 6, red))
    if rising:
        parts.append('<text x="%d" y="%.1f" fill="%s" font-size="11" '
                     'font-weight="700" text-anchor="middle">%s</text>'
                     % (ax, H - 20, red, esc(rising)))
    if note:
        parts.append(lines(note, 14, H + 18, 76, 17, fill=sub, font_size='11'))
        H += 26
    return _fig(title, cap,
        '<svg viewBox="0 0 900 %d" xmlns="http://www.w3.org/2000/svg" role="img">'
        '%s</svg>' % (H, ''.join(parts)))


# ------------------------------------------------------------------
# F12  カバー範囲の比較（どの工程まで担うか）
# ------------------------------------------------------------------
def fig_ranges(phases, rows, title, cap, dark=False, note=None):
    """rows: [(名前, 開始index, 終了index, 差し色index, 補足)]"""
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.6)' if dark else MUTED
    edge = 'rgba(255,255,255,.14)' if dark else 'rgba(46,84,150,.16)'
    track = 'rgba(255,255,255,.05)' if dark else 'rgba(46,84,150,.05)'
    X, W = 210, 660
    np_ = len(phases)
    cw = W / np_
    parts = []
    for i, ph in enumerate(phases):
        parts.append('<text x="%.1f" y="26" fill="%s" font-size="11.5" '
                     'font-weight="700" text-anchor="middle">%s</text>'
                     % (X + cw * (i + .5), sub, esc(ph)))
        if i:
            parts.append('<line x1="%.1f" y1="34" x2="%.1f" y2="%d" stroke="%s" '
                         'stroke-width="1" stroke-dasharray="3 5"/>'
                         % (X + cw * i, X + cw * i, 42 + len(rows) * 52, edge))
    y = 44
    for name, a, bmax, ai, sup in rows:
        c = ACCENTS[ai % len(ACCENTS)]
        parts.append(lines(name, 14, y + 22, 16, 16, fill=fg, font_size='12.5',
                           font_weight='700'))
        parts.append('<rect x="%d" y="%d" width="%d" height="26" rx="6" fill="%s"/>'
                     % (X, y + 4, W, track))
        parts.append('<rect class="a-grow" x="%.1f" y="%d" width="%.1f" height="26" rx="6" '
                     'fill="%s" fill-opacity=".85"/>' % (X + cw * a, y + 4, cw * (bmax - a + 1), c))
        if sup:
            parts.append(lines(sup, X + cw * a + 12, y + 22, 30, 15, fill=WHITE,
                               font_size='11'))
        y += 52
    if note:
        parts.append(lines(note, 14, y + 16, 76, 17, fill=sub, font_size='11'))
        y += 26
    return _fig(title, cap,
        '<svg viewBox="0 0 900 %d" xmlns="http://www.w3.org/2000/svg" role="img">'
        '%s</svg>' % (y + 8, ''.join(parts)))


# ------------------------------------------------------------------
# F13  組織の比較（規模を棒で、中身を箇条で）
# ------------------------------------------------------------------
def fig_orgs(items, title, cap, dark=False, unit='', note=None):
    """items: [(組織名, 規模の数値, 規模の表示, [箇条], 位置づけ, 差し色index)]"""
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.66)' if dark else MUTED
    box = 'rgba(255,255,255,.05)' if dark else WHITE
    edge = 'rgba(255,255,255,.14)' if dark else 'rgba(46,84,150,.18)'
    mx = max(v for _, v, _, _, _, _ in items) or 1
    n = len(items)
    w = int((884 - 16 - (n - 1) * 22) / n)
    parts = []
    H = 250
    for i, (name, v, disp, bullets, role, ai) in enumerate(items):
        x = 16 + i * (w + 22)
        c = ACCENTS[ai % len(ACCENTS)]
        parts.append('<rect x="%d" y="20" width="%d" height="%d" rx="12" fill="%s" '
                     'stroke="%s" stroke-width="1"/>' % (x, w, H, box, edge))
        parts.append('<rect x="%d" y="20" width="%d" height="5" rx="2.5" fill="%s"/>'
                     % (x, w, c))
        parts.append('<text x="%d" y="56" fill="%s" font-size="17" '
                     'font-weight="700">%s</text>' % (x + 18, fg, esc(name)))
        parts.append('<text x="%d" y="56" fill="%s" font-size="10.5" '
                     'font-weight="700" letter-spacing="1.4" text-anchor="end">%s</text>'
                     % (x + w - 18, c, esc(role)))
        # 規模のバー
        bw = (w - 36) * v / mx
        parts.append('<rect x="%d" y="72" width="%d" height="10" rx="5" fill="%s" '
                     'fill-opacity=".35"/>' % (x + 18, w - 36, edge))
        parts.append('<rect x="%d" y="72" width="%.1f" height="10" rx="5" fill="%s"/>'
                     % (x + 18, max(8, bw), c))
        parts.append('<text x="%d" y="106" fill="%s" font-size="15" '
                     'font-weight="700">%s</text>' % (x + 18, c, esc(disp)))
        by = 134
        for bt in bullets:
            parts.append('<circle cx="%d" cy="%d" r="2.6" fill="%s"/>'
                         % (x + 21, by - 4, c))
            ls = wrap(bt, int((w - 56) / 11.2))
            parts.append(lines(bt, x + 32, by, int((w - 56) / 11.2), 17,
                               fill=sub, font_size='11.5'))
            by += 17 * len(ls) + 8
    parts.append('<text x="16" y="14" fill="%s" font-size="10.5" font-weight="700" '
                 'letter-spacing="1.8">%s</text>' % (sub, esc(unit)))
    h = 20 + H + 16
    if note:
        parts.append(lines(note, 16, h, 78, 17, fill=sub, font_size='11'))
        h += 22
    return _fig(title, cap,
        '<svg viewBox="0 0 900 %d" xmlns="http://www.w3.org/2000/svg" role="img">'
        '%s</svg>' % (h, ''.join(parts)))


# ------------------------------------------------------------------
# F14  階段（レベルが上がるほど高くなる）
# ------------------------------------------------------------------
def fig_stairs(steps, title, cap, dark=False, note=None):
    """steps: [(レベル表記, 形, 名前, 製品, 説明, 差し色index)]"""
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.62)' if dark else MUTED
    n = len(steps)
    gap = 12
    w = int((868 - (n - 1) * gap) / n)
    BASE = 322
    parts = []
    for i, (lv, shape, name, prod, desc, ai) in enumerate(steps):
        c = ACCENTS[ai % len(ACCENTS)]
        x = 16 + i * (w + gap)
        top = BASE - (66 + i * 52)
        parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="8" fill="%s" '
                     'fill-opacity="%.2f"/>' % (x, top, w, BASE - top, c, .18 + i * .1))
        parts.append('<rect x="%d" y="%d" width="%d" height="4" rx="2" fill="%s"/>'
                     % (x, top, w, c))
        parts.append('<text x="%d" y="%d" fill="%s" font-size="10.5" '
                     'font-weight="700" letter-spacing="1.6">%s</text>'
                     % (x + 14, top + 26, c, esc(lv)))
        parts.append('<text x="%d" y="%d" fill="%s" font-size="21" '
                     'font-weight="700">%s</text>' % (x + 14, top + 54, fg, esc(shape)))
        parts.append(lines(name, x + 2, BASE + 26, 11, 17, fill=fg, font_size='12.5',
                           font_weight='700'))
        parts.append(lines(prod, x + 2, BASE + 64, 15, 15, fill=c, font_size='11',
                           font_weight='700'))
        parts.append(lines(desc, x + 2, BASE + 106, 15, 15, fill=sub, font_size='10.5'))
    parts.append('<line x1="16" y1="%d" x2="884" y2="%d" stroke="%s" '
                 'stroke-width="1.5"/>'
                 % (BASE, BASE, 'rgba(255,255,255,.2)' if dark else 'rgba(46,84,150,.25)'))
    h = BASE + 196
    if note:
        parts.append(lines(note, 16, h - 30, 76, 17, fill=sub, font_size='11'))
    return _fig(title, cap,
        '<svg viewBox="0 0 900 %d" xmlns="http://www.w3.org/2000/svg" role="img">'
        '%s</svg>' % (h, ''.join(parts)))


# ------------------------------------------------------------------
# F27  次元で見せる段階（点 → 線 → 面 → 立体）
# ------------------------------------------------------------------
def fig_dims(steps, title, cap, dark=False, note=None, split=1, uid='dims',
             marks=None,
             axis=('人がルートを決める', 'AIがルートも探索する'),
             axis_title=None,
             band=('使うAI', '任せるAI')):
    """steps: [(段階の表記, 形の種類, 名前, 製品, 説明, 差し色index)]

    形の種類は dot / line / chain / plane / cube。**その次元の図形を実際に描く。**
    「点→線→面→立体」は0次元から3次元になぞらえた比喩なので、
    棒の高さで表すより、点・線・面・立方体をそのまま出したほうが一瞬で伝わる。

    **下の帯は切らずに、紺から赤へ一続きにする。**
    「使う」と「任せる」は白黒で分かれるものではなく、
    どこまで人がルートを決めるかが少しずつ移っていくグラデーションだから。
    段ごとの短い注記は marks で渡す（['ほぼ全て人が決める', …]）。

    split は境目の位置（この番号の手前に破線を落とす）。
    同じ面に2つ置くときは uid を変える。グラデーションのidが衝突する。
    """
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.62)' if dark else MUTED
    edge = 'rgba(255,255,255,.18)' if dark else 'rgba(46,84,150,.16)'
    card = 'rgba(255,255,255,.06)' if dark else 'rgba(46,84,150,.045)'
    acc = accents(dark)
    cold = PALE if dark else NAVY          # 帯の「使う」側。暗い面では紺が沈む
    hot = ACCENTS_ON_NAVY[1] if dark else RED
    n = len(steps)
    gap = 14
    w = (868 - (n - 1) * gap) / n
    X0 = 16
    CT, CH = 16, 190                       # カードの上端と高さ
    MOTIF = CT + CH + 40                   # 矢印の意匠
    CCY, CR = CT + CH + 112, 34            # 次元の図形を囲む円
    DIMY = CCY + CR + 30                   # 点・線・面・立体
    BARY = DIMY + 18
    MARKY = BARY + 28
    parts = []

    def cx_of(i):
        return X0 + i * (w + gap) + w / 2.0

    def glyph(kind, cx, cy, c):
        o = []
        if kind == 'dot':
            o.append('<circle cx="%.1f" cy="%d" r="6" fill="%s"/>' % (cx, cy, c))
        elif kind == 'line':
            o.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" '
                     'stroke-width="2.2"/>' % (cx - 15, cy, cx + 15, cy, c))
            for dx in (-15, 15):
                o.append('<circle cx="%.1f" cy="%d" r="5" fill="%s"/>' % (cx + dx, cy, c))
        elif kind == 'chain':
            xs = [cx - 18, cx - 6, cx + 6, cx + 18]
            o.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
                     % (' '.join('%.1f,%d' % (x, cy) for x in xs), c))
            for x in xs:
                o.append('<circle cx="%.1f" cy="%d" r="4.2" fill="%s"/>' % (x, cy, c))
        elif kind == 'plane':
            o.append('<rect x="%.1f" y="%d" width="38" height="30" rx="2" fill="%s" '
                     'fill-opacity=".14" stroke="%s" stroke-width="1.8"/>'
                     % (cx - 19, cy - 15, c, c))
            o.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" '
                     'stroke-width="1" stroke-opacity=".5"/>'
                     % (cx, cy - 15, cx, cy + 15, c))
            o.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" '
                     'stroke-width="1" stroke-opacity=".5"/>'
                     % (cx - 19, cy, cx + 19, cy, c))
            for dx in (-9, 9):
                for dy in (-7, 7):
                    o.append('<circle cx="%.1f" cy="%d" r="2.6" fill="%s"/>'
                             % (cx + dx, cy + dy, c))
        elif kind == 'cube':
            top = '%.1f,%d %.1f,%d %.1f,%d %.1f,%d' % (cx - 19, cy - 7, cx, cy - 19,
                                                       cx + 19, cy - 7, cx, cy + 5)
            left = '%.1f,%d %.1f,%d %.1f,%d %.1f,%d' % (cx - 19, cy - 7, cx, cy + 5,
                                                        cx, cy + 21, cx - 19, cy + 9)
            right = '%.1f,%d %.1f,%d %.1f,%d %.1f,%d' % (cx + 19, cy - 7, cx, cy + 5,
                                                         cx, cy + 21, cx + 19, cy + 9)
            for pts, op in ((left, '.14'), (right, '.28'), (top, '.44')):
                o.append('<polygon points="%s" fill="%s" fill-opacity="%s" '
                         'stroke="%s" stroke-width="1.4" stroke-linejoin="round"/>'
                         % (pts, c, op, c))
        return ''.join(o)

    DIMNAME = {'dot': '点', 'line': '線', 'chain': '線', 'plane': '面', 'cube': '立体'}

    # 紺 → 赤の一続きの帯。座標系を固定して、5つに割っても色がつながるようにする
    parts.append('<defs><linearGradient id="%s-g" gradientUnits="userSpaceOnUse" '
                 'x1="%d" y1="0" x2="884" y2="0">'
                 '<stop offset="0" stop-color="%s"/>'
                 '<stop offset="0.5" stop-color="%s"/>'
                 '<stop offset="1" stop-color="%s"/></linearGradient></defs>'
                 % (uid, X0, cold, AZURE, hot))

    for i, (lv, kind, name, prod, desc, ai) in enumerate(steps):
        c = acc[ai % len(acc)]
        x = X0 + i * (w + gap)
        cx = cx_of(i)
        parts.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" rx="10" fill="%s" '
                     'stroke="%s" stroke-width="1"/>' % (x, CT, w, CH, card, edge))
        parts.append('<text x="%.1f" y="%d" fill="%s" font-size="9.5" font-weight="700" '
                     'letter-spacing="1.6" text-anchor="middle">%s</text>'
                     % (cx, CT + 22, c, esc(lv)))
        # 行数が段ごとに違うので、上から積み上げる。
        # 固定の座標に置くと、製品名が3行に折れた段だけ説明と重なる
        ty = CT + 46
        nl = wrap(name, 12)
        parts.append(lines(name, cx, ty, 12, 19, fill=fg, font_size='13.5',
                           font_weight='700', text_anchor='middle'))
        ty += (len(nl) - 1) * 19 + 26
        # 製品名は「／」で折る。ここは意味の切れ目なので、字数で折るより読みやすい
        pl = []
        for k, piece in enumerate(str(prod).split('／')):
            piece = piece.strip()
            if piece:
                # 幅で折る。ここには製品名（欧文）も実例（和文）も来るので、
                # 文字数で折ると和文の段だけがカードから溢れる
                pl += wrapw(piece if k == 0 else '／' + piece, 30)
        parts.append('<text x="%.1f" y="%d" fill="%s" font-size="10" font-weight="700" '
                     'text-anchor="middle">%s</text>'
                     % (cx, ty, c, ''.join('<tspan x="%.1f" dy="%s">%s</tspan>'
                                           % (cx, 0 if k == 0 else 15, esc(l))
                                           for k, l in enumerate(pl))))
        ty += (len(pl) - 1) * 15 + 22
        parts.append(lines(desc, cx, ty, 15, 14, fill=sub, font_size='10',
                           text_anchor='middle'))

        # カードから円へ落ちる破線
        parts.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" '
                     'stroke-width="1" stroke-dasharray="3 4" class="a-flow"/>'
                     % (cx, CT + CH + 6, cx, CCY - CR - 6, edge))
        # 矢印の意匠。段が進むほど、右向きの流れが強くなる
        parts.append('<g class="a-flow">')
        for k in range(3):
            tx = cx - 44 + k * 9
            parts.append('<polygon points="%.1f,%d %.1f,%d %.1f,%d" fill="%s" '
                         'fill-opacity=".55"/>'
                         % (tx, MOTIF - 4, tx + 5, MOTIF, tx, MOTIF + 4, c))
        parts.append('<circle cx="%.1f" cy="%d" r="5" fill="%s"/>' % (cx - 12, MOTIF, c))
        for k in range(3):
            bx2 = cx + 2 + k * 5
            parts.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" '
                         'stroke-width="2" stroke-opacity=".55"/>'
                         % (bx2, MOTIF - 5, bx2, MOTIF + 5, c))
        parts.append('<path d="M%.1f %d L%.1f %d M%.1f %d l-6 -6 M%.1f %d l-6 6" '
                     'stroke="%s" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
                     % (cx + 22, MOTIF, cx + 42, MOTIF, cx + 42, MOTIF, cx + 42, MOTIF, c))
        parts.append('</g>')

        parts.append('<circle cx="%.1f" cy="%d" r="%d" fill="%s" stroke="%s" '
                     'stroke-width="1" class="a-pop"/>' % (cx, CCY, CR, card, edge))
        parts.append(glyph(kind, cx, CCY, c))
        parts.append('<text x="%.1f" y="%d" fill="%s" font-size="19" font-weight="700" '
                     'text-anchor="middle">%s</text>'
                     % (cx, DIMY, fg, esc(DIMNAME.get(kind, ''))))

        parts.append('<rect x="%.1f" y="%d" width="%.1f" height="9" rx="4.5" '
                     'fill="url(#%s-g)" class="a-grow"/>' % (x, BARY, w, uid))
        if marks and i < len(marks):
            parts.append(lines(marks[i], cx, MARKY, 13, 13, fill=sub, font_size='9.5',
                               font_weight='700', text_anchor='middle'))

    # 境目。白黒では分かれないので、線ではなく細い破線で「このあたり」を示す
    bx = X0 + split * (w + gap) - gap / 2.0
    parts.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" '
                 'stroke-width="1" stroke-dasharray="4 6"/>'
                 % (bx, CT - 4, bx, BARY + 9, edge))

    h = MARKY + (28 if marks else 8)
    parts.append('<text x="%d" y="%d" fill="%s" font-size="11.5" font-weight="700" '
                 'letter-spacing="1.2">%s</text>' % (X0, h, cold if not dark else PALE,
                                                     esc(band[0])))
    parts.append('<text x="%d" y="%d" fill="%s" font-size="10">%s</text>'
                 % (X0 + 62, h, sub, esc(axis[0])))
    parts.append('<text x="884" y="%d" fill="%s" font-size="11.5" font-weight="700" '
                 'letter-spacing="1.2" text-anchor="end">%s</text>' % (h, hot, esc(band[1])))
    parts.append('<text x="%d" y="%d" fill="%s" font-size="10" text-anchor="end">%s</text>'
                 % (884 - 62, h, sub, esc(axis[1])))
    h += 12
    if axis_title:
        h += 20
        parts.append('<text x="%d" y="%d" fill="%s" font-size="10" font-weight="700" '
                     'letter-spacing="1.4">%s</text>' % (X0, h, sub, esc(axis_title)))
    if note:
        h += 20
        parts.append(lines(note, X0, h, 78, 16, fill=sub, font_size='10.5'))
        h += 16
    return _fig(title, cap,
        '<svg viewBox="0 0 900 %d" xmlns="http://www.w3.org/2000/svg" role="img">'
        '%s</svg>' % (h + 14, ''.join(parts)))


# ------------------------------------------------------------------
# F15  3カラム（並列の概念を、色分けして並べる）
# ------------------------------------------------------------------
def fig_cols(items, title, cap, dark=False):
    """items: [(英字ラベル, 名前, 一言, 本文, 差し色index)]"""
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.62)' if dark else MUTED
    box = 'rgba(255,255,255,.05)' if dark else WHITE
    edge = 'rgba(255,255,255,.14)' if dark else 'rgba(46,84,150,.2)'
    acc = accents(dark)
    n = len(items)
    gap = 20
    w = int((868 - (n - 1) * gap) / n)
    H = 214
    parts = []
    for i, (en, ja, one, txt, ai) in enumerate(items):
        c = acc[ai % len(acc)]
        x = 16 + i * (w + gap)
        parts.append('<rect x="%d" y="20" width="%d" height="%d" rx="11" fill="%s" '
                     'stroke="%s" stroke-width="1"/>' % (x, w, H, box, edge))
        parts.append('<rect x="%d" y="20" width="%d" height="5" rx="2.5" fill="%s"/>'
                     % (x, w, c))
        parts.append('<text x="%d" y="52" fill="%s" font-size="10.5" '
                     'font-weight="700" letter-spacing="1.8">%s</text>'
                     % (x + 18, c, esc(en)))
        parts.append('<text x="%d" y="82" fill="%s" font-size="17" '
                     'font-weight="700">%s</text>' % (x + 18, fg, esc(ja)))
        parts.append(lines(one, x + 18, 106, 16, 17, fill=c, font_size='12'))
        parts.append('<line x1="%d" y1="122" x2="%d" y2="122" stroke="%s" '
                     'stroke-width="1" stroke-dasharray="3 4"/>' % (x + 18, x + w - 18, edge))
        parts.append(lines(txt, x + 18, 146, int((w - 36) / 11.4), 17,
                           fill=sub, font_size='11.5'))
    return _fig(title, cap,
        '<svg viewBox="0 0 900 %d" xmlns="http://www.w3.org/2000/svg" role="img">'
        '%s</svg>' % (H + 36, ''.join(parts)))


# ==================================================================
# ここから F16〜F25。既存の15種に無い「形」を埋める。
# 投影資料では、同じ形が続くと内容の違いが見えなくなる。
# 形が変わること自体が、聴講者にとっての区切りになる。
# ==================================================================

# ------------------------------------------------------------------
# F16  横一列のプロセス（汎用のフロー。fig_issues は「壁」固定なので別に持つ）
# ------------------------------------------------------------------
def fig_flow(steps, title, cap, dark=False, uid='', note=None):
    """steps: [(見出し, 補足)] を矢印でつなぐ。3〜5個が読みやすい"""
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.62)' if dark else MUTED
    box = 'rgba(255,255,255,.06)' if dark else WHITE
    edge = 'rgba(255,255,255,.16)' if dark else 'rgba(46,84,150,.22)'
    n = len(steps)
    gap = 40
    w = int((884 - 16 - (n - 1) * gap) / n)
    H = 158
    parts = []
    for i, (h, note_) in enumerate(steps):
        x = 16 + i * (w + gap)
        parts.append('<rect x="%d" y="34" width="%d" height="%d" rx="10" fill="%s" '
                     'stroke="%s" stroke-width="1"/>' % (x, w, H, box, edge))
        parts.append('<circle cx="%d" cy="34" r="15" fill="%s"/>' % (x + w // 2, AZURE))
        parts.append('<text x="%d" y="39" fill="%s" font-size="13" font-weight="700" '
                     'text-anchor="middle">%d</text>' % (x + w // 2, WHITE, i + 1))
        parts.append(lines(h, x + 18, 84, max(6, int((w - 36) / 15.4)), 22,
                           fill=fg, font_size='15', font_weight='700'))
        parts.append(lines(note_, x + 18, 128, max(8, int((w - 36) / 11.4)), 17,
                           fill=sub, font_size='11.5'))
        if i < n - 1:
            cx = x + w + 8
            parts.append('<path d="M%d 112 L%d 112" stroke="%s" stroke-width="2" '
                         'fill="none" marker-end="url(#flw%s)"/>' % (cx, cx + gap - 18, AZURE, uid))
    h = H + 54
    if note:
        parts.append(lines(note, 16, h - 8, 76, 17, fill=sub, font_size='11'))
        h += 18
    return _fig(title, cap,
        '<svg viewBox="0 0 900 %d" xmlns="http://www.w3.org/2000/svg" role="img">'
        '<defs><marker id="flw%s" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M0 0L10 5L0 10z" fill="%s"/></marker></defs>%s</svg>'
        % (h, uid, AZURE, ''.join(parts)))


# ------------------------------------------------------------------
# F17  円環（PDCA、フィードバックループ。終わりが始まりに戻る話に）
# ------------------------------------------------------------------
def fig_cycle(steps, title, cap, dark=False, center='', uid=''):
    """steps: [(見出し, 補足)] を時計回りに配置する。4〜6個

    正円ではなく楕円に置く。16:9の面では正円だと左右が余り、
    箱を外へ逃がすと中央が空洞になる（実際、業務変革大全の
    「定着ループ」がそうなった）。輪も破線の円をただ置くのではなく、
    箱と箱のあいだを埋める弧にして矢じりを付ける。
    「回り続ける」と書いてある図が、止まって見えていた。
    """
    import math
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.62)' if dark else MUTED
    box = 'rgba(255,255,255,.06)' if dark else WHITE
    edge = 'rgba(255,255,255,.16)' if dark else 'rgba(46,84,150,.22)'
    arrow = 'rgba(255,255,255,.5)' if dark else AZURE
    hub = 'rgba(255,255,255,.10)' if dark else 'rgba(46,84,150,.07)'
    acc = accents(dark)
    uid = uid or 'cy'
    n = len(steps)
    CX, CY, RX, RY = 450, 232, 292, 148
    bw, bh = 214, 92
    ARX, ARY = 176, 92          # 弧の半径。箱の内側を、触れない距離で回る
    parts = []
    # 箱と箱のすきまを弧でつなぐ。円を1本置くだけでは、どちら回りかが出ない
    for i in range(n):
        a0 = -math.pi / 2 + 2 * math.pi * i / n
        a1 = a0 + 2 * math.pi / n
        pad = (a1 - a0) * 0.24
        sx, sy = CX + ARX * math.cos(a0 + pad), CY + ARY * math.sin(a0 + pad)
        ex, ey = CX + ARX * math.cos(a1 - pad), CY + ARY * math.sin(a1 - pad)
        parts.append('<path d="M%.1f %.1f A%d %d 0 0 1 %.1f %.1f" fill="none" '
                     'stroke="%s" stroke-width="2" stroke-dasharray="5 6" '
                     'marker-end="url(#cyc%s)"/>'
                     % (sx, sy, ARX, ARY, ex, ey, arrow, uid))
    if center:
        w = len(center) * 17 + 34
        parts.append('<rect x="%.1f" y="%d" width="%d" height="36" rx="18" fill="%s"/>'
                     % (CX - w / 2, CY - 18, w, hub))
        parts.append(lines(center, CX, CY + 6, 12, 22, fill=fg, font_size='15',
                           font_weight='700', text_anchor='middle'))
    for i, (h, note) in enumerate(steps):
        a = -math.pi / 2 + 2 * math.pi * i / n
        x = CX + RX * math.cos(a) - bw / 2
        y = CY + RY * math.sin(a) - bh / 2
        x = max(8, min(892 - bw, x))
        c = acc[i % len(acc)]
        parts.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="9" fill="%s" '
                     'stroke="%s" stroke-width="1"/>' % (x, y, bw, bh, box, edge))
        parts.append('<rect x="%.1f" y="%.1f" width="4" height="%d" rx="2" fill="%s"/>'
                     % (x, y, bh, c))
        parts.append('<text x="%.1f" y="%.1f" fill="%s" font-size="10.5" '
                     'font-weight="700" letter-spacing="1.4">%02d</text>'
                     % (x + 16, y + 25, c, i + 1))
        parts.append(lines(h, x + 44, y + 27, 12, 18, fill=fg, font_size='13.5',
                           font_weight='700'))
        parts.append(lines(note, x + 16, y + 54, 16, 15, fill=sub, font_size='11'))
    h = int(CY + RY + bh / 2 + 22)
    return _fig(title, cap,
        '<svg viewBox="0 0 900 %d" xmlns="http://www.w3.org/2000/svg" role="img">'
        '<defs><marker id="cyc%s" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M0 0L10 5L0 10z" fill="%s"/></marker></defs>%s</svg>'
        % (h, uid, arrow, ''.join(parts)))


# ------------------------------------------------------------------
# F26  2×2の循環（SECI、OODA、PDCAのように4象限を回るもの）
# ------------------------------------------------------------------
def fig_loop4(items, title, cap, dark=False, uid='', edge_labels=None, note=None):
    """items: [(見出し, 英名, 説明, [中の項目, ...])] を左上→右上→右下→左下の順に4つ。

    円環の fig_cycle と違い、4象限に置いて外周を矢印が回る形。
    「暗黙知 → 形式知 → 暗黙知」のように、辺ごとに状態が変わる循環に向く。
    edge_labels は上・右・下・左の辺に置く4つのラベル（省略可）。
    """
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.66)' if dark else MUTED
    box = 'rgba(255,255,255,.055)' if dark else WHITE
    chip = 'rgba(255,255,255,.08)' if dark else 'rgba(46,84,150,.06)'
    edge = 'rgba(255,255,255,.18)' if dark else 'rgba(46,84,150,.22)'
    mid = 'rgba(255,255,255,.5)' if dark else AZURE
    uid = uid or 'l4'
    BW, BH, GX, GY = 372, 208, 46, 74
    X0, Y0 = 62, 64
    pos = [(X0, Y0), (X0 + BW + GX, Y0),
           (X0 + BW + GX, Y0 + BH + GY), (X0, Y0 + BH + GY)]
    parts = ['<defs><marker id="l4a%s" markerWidth="9" markerHeight="9" refX="7" refY="4.5" '
             'orient="auto"><path d="M0 0 L9 4.5 L0 9 z" fill="%s"/></marker></defs>'
             % (uid, mid)]
    for i, (h, en, desc, chips) in enumerate(items[:4]):
        x, y = pos[i]
        c = ACCENTS[i % len(ACCENTS)]
        parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="12" fill="%s" '
                     'stroke="%s" stroke-width="1.4"/>' % (x, y, BW, BH, box, edge))
        parts.append('<rect x="%d" y="%d" width="%d" height="4" rx="2" fill="%s"/>'
                     % (x, y, BW, c))
        parts.append('<text x="%d" y="%d" fill="%s" font-size="16" font-weight="700">%s</text>'
                     % (x + 20, y + 36, fg, esc(h)))
        parts.append('<text x="%d" y="%d" fill="%s" font-size="10.5" font-weight="700" '
                     'letter-spacing="1.2">%s</text>' % (x + 20, y + 54, c, esc(en)))
        parts.append(lines(desc, x + 20, y + 78, 30, 16, fill=sub, font_size='11.5'))
        cy = y + 78 + max(1, len(wrap(desc, 30))) * 16 + 12
        for j, t in enumerate(chips[:4]):
            cx = x + 20 + (j % 2) * ((BW - 52) / 2 + 12)
            yy = cy + (j // 2) * 30
            parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="23" rx="5" fill="%s"/>'
                         % (cx, yy, (BW - 52) / 2, chip))
            parts.append('<text x="%.1f" y="%.1f" fill="%s" font-size="10.5">%s</text>'
                         % (cx + 10, yy + 15.5, fg, esc(t[:13])))
    # 外周を回る矢印。上→右→下→左。
    #
    # **辺いっぱいに引く。** もとは箱の隅から隣の箱の中心までしか引いておらず、
    # 4本が短い破線として宙に浮き、「回っている」ことがまったく伝わらなかった。
    # それぞれの辺を、箱の中心から隣の箱の中心まで通すと輪として読める。
    W = X0 * 2 + BW * 2 + GX
    H = Y0 + BH * 2 + GY + 64
    M = 26                                   # 箱の外側に取る余白
    L, R = X0, X0 + BW * 2 + GX              # 箱の並びの左端・右端
    T, Bm = Y0, Y0 + BH * 2 + GY             # 箱の並びの上端・下端
    arcs = ['M%.1f %d H%.1f' % (L + BW / 2, T - M, R - BW / 2),      # 上 →
            'M%d %.1f V%.1f' % (R + M, T + BH / 2, Bm - BH / 2),     # 右 ↓
            'M%.1f %d H%.1f' % (R - BW / 2, Bm + M, L + BW / 2),     # 下 ←
            'M%d %.1f V%.1f' % (L - M, Bm - BH / 2, T + BH / 2)]     # 左 ↑
    for d in arcs:
        parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6" '
                     'stroke-dasharray="7 5" marker-end="url(#l4a%s)"/>' % (d, mid, uid))
    if edge_labels:
        # ラベルは、その辺の矢印の真ん中に置く。
        # もとは箱と箱の隙間の座標に置いていたので、矢印から離れて浮いていた
        spots = [(W / 2, T - M - 12), (R + M + 15, (T + Bm) / 2),
                 (W / 2, Bm + M + 20), (L - M - 15, (T + Bm) / 2)]
        for k, t in enumerate(edge_labels[:4]):
            sx, sy = spots[k]
            if k % 2:
                # 左右の辺は横幅がほとんど無い。4文字を超えると画面の外へ出て
                # 頭が切れる（「一周して、前より深く」が「り深く」になった）。
                # 縦の辺には縦の余白があるので、90度倒して真ん中に置く
                parts.append('<text x="0" y="0" fill="%s" font-size="11.5" '
                             'font-weight="700" text-anchor="middle" '
                             'transform="translate(%.1f %.1f) rotate(-90)">%s</text>'
                             % (mid, sx, sy, esc(t)))
            else:
                parts.append('<text x="%.1f" y="%.1f" fill="%s" font-size="11.5" '
                             'font-weight="700" text-anchor="middle">%s</text>'
                             % (sx, sy, mid, esc(t)))
    if note:
        H += 26
        parts.append('<text x="%d" y="%d" fill="%s" font-size="11">%s</text>'
                     % (X0, H - 12, sub, esc(note)))
    return _fig(title, cap,
        '<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" role="img">'
        '%s</svg>' % (W, H, ''.join(parts)))


# ------------------------------------------------------------------
# F18  構成比のドーナツ（1つの全体を分けて見せる）
# ------------------------------------------------------------------
def fig_donut(items, title, cap, dark=False, center='', note=None):
    """items: [(名前, 数値, 補足)]。数値の合計を100%として扱う"""
    import math
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.62)' if dark else MUTED
    ring = 'rgba(255,255,255,.08)' if dark else 'rgba(46,84,150,.08)'
    total = sum(v for _, v, _ in items) or 1
    CX, CY, R, TH = 200, 180, 128, 44
    parts = ['<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" stroke-width="%d"/>'
             % (CX, CY, R, ring, TH)]
    a0 = -math.pi / 2
    for i, (name, v, _) in enumerate(items):
        sweep = 2 * math.pi * v / total
        a1 = a0 + sweep
        large = 1 if sweep > math.pi else 0
        x0, y0 = CX + R * math.cos(a0), CY + R * math.sin(a0)
        x1, y1 = CX + R * math.cos(a1), CY + R * math.sin(a1)
        parts.append('<path class="a-draw" d="M%.1f %.1f A%d %d 0 %d 1 %.1f %.1f" fill="none" '
                     'stroke="%s" stroke-width="%d" stroke-opacity=".92"/>'
                     % (x0, y0, R, R, large, x1, y1, ACCENTS[i % len(ACCENTS)], TH))
        a0 = a1
    if center:
        parts.append(lines(center, CX, CY + 2, 8, 22, fill=fg, font_size='16',
                           font_weight='700', text_anchor='middle'))
    # 凡例は右側に縦積み
    y = 56
    for i, (name, v, sup) in enumerate(items):
        c = ACCENTS[i % len(ACCENTS)]
        parts.append('<rect x="410" y="%d" width="12" height="12" rx="3" fill="%s"/>'
                     % (y - 11, c))
        parts.append('<text x="432" y="%d" fill="%s" font-size="14" '
                     'font-weight="700">%s</text>' % (y, fg, esc(name)))
        parts.append('<text x="862" y="%d" fill="%s" font-size="15" font-weight="700" '
                     'text-anchor="end">%d%%</text>' % (y, c, round(v * 100 / total)))
        if sup:
            parts.append(lines(sup, 432, y + 20, 44, 16, fill=sub, font_size='11'))
            y += 58
        else:
            y += 40
    h = max(340, y + 16)
    if note:
        parts.append(lines(note, 16, h - 6, 76, 17, fill=sub, font_size='11'))
        h += 16
    return _fig(title, cap,
        '<svg viewBox="0 0 900 %d" xmlns="http://www.w3.org/2000/svg" role="img">'
        '%s</svg>' % (h, ''.join(parts)))


# ------------------------------------------------------------------
# F19  積み上げ棒（複数の対象を、内訳ごと比べる）
# ------------------------------------------------------------------
def fig_stack(rows, keys, title, cap, dark=False, unit='', note=None):
    """rows: [(対象名, [各内訳の数値])]、keys: [内訳の名前]"""
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.62)' if dark else MUTED
    track = 'rgba(255,255,255,.06)' if dark else 'rgba(46,84,150,.06)'
    X, W = 210, 600
    mx = max(sum(v) for _, v in rows) or 1
    parts = []
    # 凡例
    lx = X
    for i, k in enumerate(keys):
        parts.append('<rect x="%d" y="14" width="11" height="11" rx="3" fill="%s"/>'
                     % (lx, ACCENTS[i % len(ACCENTS)]))
        parts.append('<text x="%d" y="24" fill="%s" font-size="11.5">%s</text>'
                     % (lx + 17, sub, esc(k)))
        lx += 24 + len(k) * 12
    y = 46
    for name, vals in rows:
        parts.append(lines(name, 14, y + 22, 15, 17, fill=fg, font_size='13',
                           font_weight='700'))
        parts.append('<rect x="%d" y="%d" width="%d" height="30" rx="6" fill="%s"/>'
                     % (X, y + 4, W, track))
        cx = X
        for i, v in enumerate(vals):
            w = W * v / mx
            if w < 1:
                continue
            parts.append('<rect class="a-grow" x="%.1f" y="%d" width="%.1f" height="30" '
                         'fill="%s" fill-opacity=".9"/>' % (cx, y + 4, w, ACCENTS[i % len(ACCENTS)]))
            if w > 46:
                parts.append('<text x="%.1f" y="%d" fill="%s" font-size="11.5" '
                             'font-weight="700" text-anchor="middle">%s</text>'
                             % (cx + w / 2, y + 24, WHITE, esc(str(v))))
            cx += w
        parts.append('<text x="%d" y="%d" fill="%s" font-size="12.5" '
                     'font-weight="700">%s</text>' % (X + W + 12, y + 24, fg, sum(vals)))
        y += 46
    if unit:
        parts.append('<text x="%d" y="24" fill="%s" font-size="10.5" font-weight="700" '
                     'letter-spacing="1.6" text-anchor="end">%s</text>' % (884, sub, esc(unit)))
    if note:
        parts.append(lines(note, 14, y + 14, 76, 17, fill=sub, font_size='11'))
        y += 26
    return _fig(title, cap,
        '<svg viewBox="0 0 900 %d" xmlns="http://www.w3.org/2000/svg" role="img">'
        '%s</svg>' % (y + 10, ''.join(parts)))


# ------------------------------------------------------------------
# F20  格子（行×列。どこが該当するかを印で示す）
# ------------------------------------------------------------------
def fig_matrix(cols, rows, title, cap, dark=False, note=None):
    """rows: [(行名, [各列の値])]。値は '' / '○' / '△' / '×' か短い文字列"""
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.66)' if dark else MUTED
    grid = 'rgba(255,255,255,.14)' if dark else 'rgba(46,84,150,.18)'
    zebra = 'rgba(255,255,255,.035)' if dark else 'rgba(46,84,150,.035)'
    tone = {'○': '#2f8f8a', '◎': AZURE, '△': '#c9762f', '×': RED, '－': sub}
    X0, LW, W = 14, 250, 872
    cw = (W - LW) / len(cols)
    parts = []
    for i, c in enumerate(cols):
        parts.append(lines(c, X0 + LW + cw * (i + .5), 26, 9, 15, fill=sub,
                           font_size='11.5', font_weight='700', text_anchor='middle'))
    y = 40
    for r, (name, vals) in enumerate(rows):
        nl = len(wrap(name, 20))
        h = 22 + nl * 17
        if r % 2:
            parts.append('<rect x="%d" y="%.1f" width="%d" height="%.1f" fill="%s"/>'
                         % (X0, y, W, h, zebra))
        parts.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" '
                     'stroke-width="1"/>' % (X0, y, X0 + W, y, grid))
        parts.append(lines(name, X0 + 10, y + 20, 20, 17, fill=fg, font_size='12.5',
                           font_weight='700'))
        for i, v in enumerate(vals):
            if not v:
                continue
            col = tone.get(v, fg)
            size = '17' if v in tone else '11.5'
            parts.append('<text x="%.1f" y="%.1f" fill="%s" font-size="%s" '
                         'font-weight="700" text-anchor="middle">%s</text>'
                         % (X0 + LW + cw * (i + .5), y + 22, col, size, esc(v)))
        y += h
    parts.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" '
                 'stroke-width="1"/>' % (X0, y, X0 + W, y, grid))
    for i in range(len(cols) + 1):
        x = X0 + LW + cw * i
        parts.append('<line x1="%.1f" y1="32" x2="%.1f" y2="%.1f" stroke="%s" '
                     'stroke-width="1"/>' % (x, x, y, grid))
    if note:
        y += 22
        parts.append(lines(note, X0, y, 78, 17, fill=sub, font_size='11'))
        y += 8
    return _fig(title, cap,
        '<svg viewBox="0 0 900 %.0f" xmlns="http://www.w3.org/2000/svg" role="img">'
        '%s</svg>' % (y + 10, ''.join(parts)))


# ------------------------------------------------------------------
# F21  大きな数字（3〜4個。投影でいちばん効く形）
# ------------------------------------------------------------------
def fig_stats(items, title, cap, dark=False, note=None):
    """items: [(数値, 単位, 何の数字か, 出典や補足, 差し色index)]"""
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.62)' if dark else MUTED
    edge = 'rgba(255,255,255,.16)' if dark else 'rgba(46,84,150,.2)'
    n = len(items)
    gap = 20
    w = int((868 - (n - 1) * gap) / n)
    H = 176
    parts = []
    for i, (num, unit, what, sup, ai) in enumerate(items):
        c = ACCENTS[ai % len(ACCENTS)]
        x = 16 + i * (w + gap)
        parts.append('<rect x="%d" y="16" width="%d" height="%d" rx="11" fill="none" '
                     'stroke="%s" stroke-width="1"/>' % (x, w, H, edge))
        parts.append('<rect x="%d" y="16" width="%d" height="5" rx="2.5" fill="%s"/>'
                     % (x, w, c))
        size = 52 if len(str(num)) <= 4 else (40 if len(str(num)) <= 7 else 30)
        parts.append('<text x="%d" y="86" fill="%s" font-size="%d" font-weight="700" '
                     'letter-spacing="-1">%s</text>' % (x + 20, c, size, esc(str(num))))
        if unit:
            parts.append('<text x="%d" y="86" fill="%s" font-size="15" '
                         'font-weight="700">%s</text>'
                         % (x + 24 + int(len(str(num)) * size * 0.56), sub, esc(unit)))
        parts.append(lines(what, x + 20, 118, max(8, int((w - 40) / 14.4)), 20,
                           fill=fg, font_size='14', font_weight='700'))
        if sup:
            parts.append(lines(sup, x + 20, 158, max(10, int((w - 40) / 11.4)), 15,
                               fill=sub, font_size='11'))
    h = H + 42
    if note:
        parts.append(lines(note, 16, h - 6, 76, 17, fill=sub, font_size='11'))
        h += 16
    return _fig(title, cap,
        '<svg viewBox="0 0 900 %d" xmlns="http://www.w3.org/2000/svg" role="img">'
        '%s</svg>' % (h, ''.join(parts)))


# ------------------------------------------------------------------
# F22  二項対立（どちらを選ぶか、という話の形）
# ------------------------------------------------------------------
def fig_versus(left, right, rows, title, cap, dark=False):
    """left/right: (見出し, ひとこと)、rows: [(観点, 左の内容, 右の内容)]"""
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.62)' if dark else MUTED
    edge = 'rgba(255,255,255,.16)' if dark else 'rgba(46,84,150,.2)'
    lbg = 'rgba(46,84,150,.10)' if not dark else 'rgba(255,255,255,.06)'
    rbg = 'rgba(226,55,68,.08)' if not dark else 'rgba(255,93,106,.10)'
    LX, BW = 200, 330
    RX = LX + BW + 24                     # 箱が重ならないよう間を空ける
    MID = LX + BW + 12
    parts = []
    for x, (h, one), bg, c in ((LX, left, lbg, AZURE), (RX, right, rbg, RED)):
        parts.append('<rect x="%d" y="14" width="%d" height="72" rx="10" fill="%s"/>'
                     % (x, BW, bg))
        parts.append('<rect x="%d" y="14" width="%d" height="4" rx="2" fill="%s"/>'
                     % (x, BW, c))
        parts.append(lines(h, x + 20, 46, 18, 22, fill=fg, font_size='16',
                           font_weight='700'))
        parts.append(lines(one, x + 20, 72, 26, 16, fill=c, font_size='11.5',
                           font_weight='700'))
    parts.append('<text x="%d" y="55" fill="%s" font-size="11" font-weight="700" '
                 'letter-spacing="1" text-anchor="middle">VS</text>' % (MID, sub))
    y = 104
    for k, a, b in rows:
        nl = max(len(wrap(a, 25)), len(wrap(b, 25)), len(wrap(k, 14)))
        h = 16 + nl * 19
        parts.append('<line x1="14" y1="%.1f" x2="884" y2="%.1f" stroke="%s" '
                     'stroke-width="1"/>' % (y, y, edge))
        parts.append(lines(k, 14, y + 24, 14, 18, fill=sub, font_size='12',
                           font_weight='700'))
        parts.append(lines(a, LX + 20, y + 24, 25, 19, fill=fg, font_size='12.5'))
        parts.append(lines(b, RX + 20, y + 24, 25, 19, fill=fg, font_size='12.5'))
        parts.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" '
                     'stroke-width="1"/>' % (MID, y, MID, y + h, edge))
        y += h
    parts.append('<line x1="14" y1="%.1f" x2="884" y2="%.1f" stroke="%s" '
                 'stroke-width="1"/>' % (y, y, edge))
    return _fig(title, cap,
        '<svg viewBox="0 0 900 %.0f" xmlns="http://www.w3.org/2000/svg" role="img">'
        '%s</svg>' % (y + 14, ''.join(parts)))


# ------------------------------------------------------------------
# F23  階層ツリー（分類・組織・構造。2段まで）
# ------------------------------------------------------------------
def fig_tree(root, branches, title, cap, dark=False, uid=''):
    """root: 頂点の名前、branches: [(枝の名前, [葉, ...])] 最大4本"""
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.62)' if dark else MUTED
    box = 'rgba(255,255,255,.06)' if dark else WHITE
    edge = 'rgba(255,255,255,.16)' if dark else 'rgba(46,84,150,.22)'
    n = len(branches)
    gap = 18
    w = int((868 - (n - 1) * gap) / n)
    parts = []
    parts.append('<rect x="300" y="14" width="300" height="52" rx="10" fill="%s"/>' % AZURE)
    parts.append(lines(root, 450, 46, 20, 20, fill=WHITE, font_size='15',
                       font_weight='700', text_anchor='middle'))
    maxleaf = max(len(l) for _, l in branches)
    for i, (name, leaves) in enumerate(branches):
        c = ACCENTS[i % len(ACCENTS)]
        x = 16 + i * (w + gap)
        cx = x + w // 2
        parts.append('<path d="M450 66 L450 88 L%d 88 L%d 110" stroke="%s" '
                     'stroke-width="1.5" fill="none"/>' % (cx, cx, edge))
        parts.append('<rect x="%d" y="110" width="%d" height="46" rx="9" fill="%s" '
                     'stroke="%s" stroke-width="1"/>' % (x, w, box, edge))
        parts.append('<rect x="%d" y="110" width="%d" height="4" rx="2" fill="%s"/>'
                     % (x, w, c))
        parts.append(lines(name, cx, 138, max(7, int(w / 15.4)), 18, fill=fg,
                           font_size='13.5', font_weight='700', text_anchor='middle'))
        ly = 176
        for leaf in leaves:
            parts.append('<rect x="%d" y="%d" width="%d" height="36" rx="7" fill="%s" '
                         'fill-opacity=".10"/>' % (x + 10, ly, w - 20, c))
            parts.append(lines(leaf, x + 22, ly + 22, max(8, int((w - 44) / 11.6)), 15,
                               fill=sub, font_size='11.5'))
            ly += 44
    return _fig(title, cap,
        '<svg viewBox="0 0 900 %d" xmlns="http://www.w3.org/2000/svg" role="img">'
        '%s</svg>' % (176 + maxleaf * 44 + 12, ''.join(parts)))


# ------------------------------------------------------------------
# F24  2軸の位置づけ（点を置く。4象限より自由度が高い）
# ------------------------------------------------------------------
def fig_map(xlab, ylab, points, title, cap, dark=False, corners=None):
    """points: [(名前, x0-100, y0-100, 差し色index, 補足)]"""
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.62)' if dark else MUTED
    edge = 'rgba(255,255,255,.16)' if dark else 'rgba(46,84,150,.2)'
    grid = 'rgba(255,255,255,.07)' if dark else 'rgba(46,84,150,.07)'
    X0, Y0, W, H = 96, 40, 700, 320
    parts = []
    for i in range(1, 4):
        parts.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" '
                     'stroke-width="1"/>' % (X0, Y0 + H * i / 4, X0 + W, Y0 + H * i / 4, grid))
        parts.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" '
                     'stroke-width="1"/>' % (X0 + W * i / 4, Y0, X0 + W * i / 4, Y0 + H, grid))
    parts.append('<path d="M%d %d L%d %d L%d %d" stroke="%s" stroke-width="1.5" '
                 'fill="none"/>' % (X0, Y0, X0, Y0 + H, X0 + W, Y0 + H, edge))
    if corners:
        for (cx, cy, txt) in corners:
            parts.append(lines(txt, X0 + W * cx / 100, Y0 + H * (100 - cy) / 100, 14, 15,
                               fill=sub, font_size='10.5', text_anchor='middle'))
    for name, px, py, ai, sup in points:
        c = ACCENTS[ai % len(ACCENTS)]
        x = X0 + W * px / 100
        y = Y0 + H * (100 - py) / 100
        parts.append('<circle class="a-pop" style="--o:%.1fpx %.1fpx" cx="%.1f" cy="%.1f" '
                     'r="9" fill="%s" fill-opacity=".9"/>' % (x, y, x, y, c))
        parts.append('<circle cx="%.1f" cy="%.1f" r="16" fill="%s" fill-opacity=".14"/>'
                     % (x, y, c))
        parts.append(lines(name, x, y - 24, 16, 16, fill=fg, font_size='12.5',
                           font_weight='700', text_anchor='middle'))
        if sup:
            parts.append(lines(sup, x, y + 32, 18, 14, fill=sub, font_size='10.5',
                               text_anchor='middle'))
    parts.append('<text x="%d" y="%d" fill="%s" font-size="12" font-weight="700" '
                 'text-anchor="middle">%s</text>' % (X0 + W // 2, Y0 + H + 34, sub, esc(xlab)))
    ysafe = ''.join(c for c in ylab if c not in '↑↓←→')
    parts.append('<text x="0" y="0" fill="%s" font-size="12" font-weight="700" '
                 'text-anchor="middle" transform="translate(30 %d) rotate(-90)">%s</text>'
                 % (sub, Y0 + H // 2, esc(ysafe)))
    return _fig(title, cap,
        '<svg viewBox="0 0 900 %d" xmlns="http://www.w3.org/2000/svg" role="img">'
        '%s</svg>' % (Y0 + H + 52, ''.join(parts)))


# ------------------------------------------------------------------
# F25  判定リスト（やること・やらないこと、可否の一覧）
# ------------------------------------------------------------------
def fig_check(items, title, cap, dark=False, note=None):
    """items: [(可否 True/False/None, 見出し, 補足)]"""
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.62)' if dark else MUTED
    okbg = 'rgba(47,143,138,.10)'
    ngbg = 'rgba(226,55,68,.09)'
    nabg = 'rgba(46,84,150,.07)' if not dark else 'rgba(255,255,255,.05)'
    parts = []
    y = 16
    for ok, h, sup in items:
        c = TEAL if ok is True else (RED if ok is False else MUTED)
        bg = okbg if ok is True else (ngbg if ok is False else nabg)
        mark = '○' if ok is True else ('×' if ok is False else '－')
        nl = max(len(wrap(h, 34)), 1) + (len(wrap(sup, 62)) if sup else 0)
        bh = 20 + nl * 20
        parts.append('<rect x="14" y="%.1f" width="870" height="%.1f" rx="9" fill="%s"/>'
                     % (y, bh, bg))
        parts.append('<rect x="14" y="%.1f" width="4" height="%.1f" rx="2" fill="%s"/>'
                     % (y, bh, c))
        parts.append('<text x="42" y="%.1f" fill="%s" font-size="18" '
                     'font-weight="700">%s</text>' % (y + 30, c, mark))
        parts.append(lines(h, 76, y + 28, 34, 20, fill=fg, font_size='14',
                           font_weight='700'))
        if sup:
            parts.append(lines(sup, 76, y + 28 + len(wrap(h, 34)) * 20, 62, 18,
                               fill=sub, font_size='11.5'))
        y += bh + 10
    if note:
        parts.append(lines(note, 14, y + 14, 76, 17, fill=sub, font_size='11'))
        y += 26
    return _fig(title, cap,
        '<svg viewBox="0 0 900 %.0f" xmlns="http://www.w3.org/2000/svg" role="img">'
        '%s</svg>' % (y + 8, ''.join(parts)))
