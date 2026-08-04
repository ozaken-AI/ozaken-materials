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


def lines(text, x, y, n, lh, **kw):
    """折り返した複数行のtspanを持つtext要素"""
    attrs = ' '.join('%s="%s"' % (k.replace('_', '-'), v) for k, v in kw.items())
    ls = wrap(text, n)
    ts = ''.join('<tspan x="%s" dy="%s">%s</tspan>'
                 % (x, 0 if i == 0 else lh, esc(l)) for i, l in enumerate(ls))
    return '<text x="%s" y="%s" %s>%s</text>' % (x, y, attrs, ts)


def _fig(title, cap, svg):
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
def fig_quad(xlab, ylab, cells, title, cap, dark=False):
    """cells: [(見出し, 補足, 危険度0-2)] を左上→右上→左下→右下の順で4つ"""
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.6)' if dark else MUTED
    edge = 'rgba(255,255,255,.16)' if dark else 'rgba(46,84,150,.22)'
    tone = [('rgba(46,84,150,.16)', AZURE), ('rgba(226,55,68,.12)', '#c9762f'),
            ('rgba(226,55,68,.18)', RED)]
    parts = []
    for i, (h, note, lv) in enumerate(cells):
        cx = 120 + (i % 2) * 372
        cy = 56 + (i // 2) * 168
        bg, bar = tone[lv]
        parts.append('<rect x="%d" y="%d" width="356" height="152" rx="10" '
                     'fill="%s" stroke="%s" stroke-width="1"/>' % (cx, cy, bg, edge))
        parts.append('<rect x="%d" y="%d" width="356" height="4" rx="2" fill="%s"/>'
                     % (cx, cy, bar))
        parts.append(lines(h, cx + 20, cy + 40, 17, 24, fill=fg, font_size='15',
                           font_weight='700'))
        parts.append(lines(note, cx + 20, cy + 90, 21, 19, fill=sub, font_size='12'))
    parts.append('<text x="470" y="24" fill="%s" font-size="12" font-weight="700" '
                 'text-anchor="middle">%s</text>' % (sub, esc(xlab)))
    # 回転テキストに矢印グリフを入れると向きが破綻するため、必ず落とす
    ysafe = ''.join(c for c in ylab if c not in '↑↓←→')
    parts.append('<text x="0" y="0" fill="%s" font-size="12" font-weight="700" '
                 'text-anchor="middle" transform="translate(28 200) rotate(-90)">%s</text>'
                 % (sub, esc(ysafe)))
    parts.append('<path d="M96 380 L96 40" stroke="%s" stroke-width="1" fill="none"/>' % edge)
    parts.append('<path d="M96 380 L884 380" stroke="%s" stroke-width="1" fill="none"/>' % edge)
    return _fig(title, cap,
        '<svg viewBox="0 0 900 396" xmlns="http://www.w3.org/2000/svg" role="img">'
        '%s</svg>' % ''.join(parts))


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
        parts.append('<rect x="%d" y="%d" width="%.1f" height="26" rx="5" fill="%s" '
                     'fill-opacity="%.2f"/>' % (X, y + 4, w, tone[lv], .9 if lv else .8))
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


# ------------------------------------------------------------------
# F10  年表（時間の流れと、主体ごとの色分け）
# ------------------------------------------------------------------
def fig_timeline(events, title, cap, dark=False, axis='2026年5月'):
    """events: [(日付, 主体, 出来事, 意味, 差し色index)]"""
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.68)' if dark else MUTED
    box = 'rgba(255,255,255,.05)' if dark else WHITE
    edge = 'rgba(255,255,255,.14)' if dark else 'rgba(46,84,150,.18)'
    n = len(events)
    w = int((884 - 16 - (n - 1) * 20) / n)
    LY = 66
    parts = ['<line x1="16" y1="%d" x2="884" y2="%d" stroke="%s" stroke-width="2"/>'
             % (LY, LY, edge)]
    parts.append('<text x="16" y="26" fill="%s" font-size="11" font-weight="700" '
                 'letter-spacing="2.4">%s</text>' % (sub, esc(axis)))
    for i, (date, who, what, mean, ai) in enumerate(events):
        x = 16 + i * (w + 20)
        c = ACCENTS[ai % len(ACCENTS)]
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
                        CX - wb / 2, y + H - 10, c, .22 + i * .06, c))
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
        parts.append('<rect x="%.1f" y="%d" width="%.1f" height="26" rx="6" fill="%s" '
                     'fill-opacity=".85"/>' % (X + cw * a, y + 4, cw * (bmax - a + 1), c))
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
# F15  3カラム（並列の概念を、色分けして並べる）
# ------------------------------------------------------------------
def fig_cols(items, title, cap, dark=False):
    """items: [(英字ラベル, 名前, 一言, 本文, 差し色index)]"""
    fg = WHITE if dark else INK
    sub = 'rgba(255,255,255,.62)' if dark else MUTED
    box = 'rgba(255,255,255,.05)' if dark else WHITE
    edge = 'rgba(255,255,255,.14)' if dark else 'rgba(46,84,150,.2)'
    n = len(items)
    gap = 20
    w = int((868 - (n - 1) * gap) / n)
    H = 214
    parts = []
    for i, (en, ja, one, txt, ai) in enumerate(items):
        c = ACCENTS[ai % len(ACCENTS)]
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
