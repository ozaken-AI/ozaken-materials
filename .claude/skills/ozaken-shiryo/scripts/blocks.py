#!/usr/bin/env python3
"""本文に置ける部品（ブロック）。図版でも、カードでもないもの。

**なぜ page_parts と分けたか。**
page_parts は「資料の骨格」（扉・節・締め・カード）を持つ。
こちらは骨格の中に置く**中身の型**で、数が増えていく。
同じファイルに混ぜると、骨格を直したいときに探せなくなる。

    from blocks import bignum, quote, steps, callout, ...

**動きの作法は、5つのサンプル集から取った。**
（Animation Dictionary / Kinetics / Amicro / Animista / Transitions.dev）
そのまま貼れる形のものは一つも無かった。React前提か、
配色が資料アーカイブの規定から外れているかのどちらかなので、
**技法だけを抜き出して、規定の色と書体で組み直した**。

借りた技法と、その理由。

  ・帯の伸びは width ではなく transform:scaleX。
    width を動かすと毎フレーム再レイアウトが走る
  ・光沢は background-position を動かす。擬似要素を走らせる手もあるが、
    そちらは要素ごとに overflow:hidden が要る
  ・並んだものの周期は、互いに割り切れない秒数にする。
    割り切れると数秒ごとに整列し直して、作り物に見える
  ・立ち上がりは、行そのものを窓にして下から出す（overflow:hidden）
  ・遅延は --i ひとつで配る。段ごとに書かない

**色は PALETTE の中だけ。** ここを外すと check_tokens が公開を止める。
書体も3つの変数だけ。CSSは tpl_style.html の末尾に置いてある。
"""
from domain_fig import esc


# ══════════════════════════════════════════════════ 数字を見せる

def bignum(value, unit, label, note=None, tone='azure'):
    """ひとつの数字を、画面いっぱいで見せる。

    投影で数字が主役になる面に置く。tone は azure / red / teal。
    **数字は英字の書体で組む。** 和文書体の数字は幅が揃わず、
    大きくすると並びが崩れて見える。
    """
    return ('<div class="bignum bn-%s" data-reveal>\n'
            '  <div class="bn-v"><b>%s</b><i>%s</i></div>\n'
            '  <p class="bn-l">%s</p>\n%s</div>\n'
            % (tone, esc(value), esc(unit), esc(label),
               '  <p class="bn-n">%s</p>\n' % esc(note) if note else ''))


def statgrid(items):
    """数字の札を並べる。items: [(数値, 単位, 何の数字か)]。3〜4個。

    **単位は数値の右下に小さく置く。** 同じ大きさで並べると、
    どこまでが数字なのかが一目で分からなくなる。
    """
    cells = ''.join(
        '  <div class="sg-i"><div class="sg-v"><b>%s</b><i>%s</i></div>'
        '<p>%s</p></div>\n' % (esc(v), esc(u), esc(l)) for v, u, l in items)
    return '<div class="statgrid" data-reveal>\n%s</div>\n' % cells


def meters(items, note=None):
    """割合の帯。items: [(ラベル, 0〜100の数値, 表示する値)]。

    **帯は scaleX で伸ばす。** width を動かすと毎フレーム再レイアウトが走る。
    画面に入ってから伸びるので、数の差が「動きの差」として見える。
    """
    rows = ''.join(
        '  <div class="mt-r"><span class="mt-l">%s</span>'
        '<span class="mt-t"><i style="--w:%s"></i></span>'
        '<span class="mt-v">%s</span></div>\n'
        % (esc(l), max(0, min(100, int(n))) / 100.0, esc(v))
        for l, n, v in items)
    return ('<div class="meters" data-reveal>\n%s%s</div>\n'
            % (rows, '  <p class="mt-n">%s</p>\n' % esc(note) if note else ''))


def kpi_row(items):
    """前と後を、矢印でつないで見せる。items: [(何の値か, 前, 後)]。

    数字の変化そのものが主役のときに使う。棒グラフにするほどの
    データが無い、でも「変わった」ことは見せたい、という場面。
    """
    cells = ''.join(
        '  <div class="kp-i"><p class="kp-k">%s</p>'
        '<div class="kp-b"><span class="kp-a">%s</span>'
        '<span class="kp-ar" aria-hidden="true"></span>'
        '<span class="kp-z">%s</span></div></div>\n'
        % (esc(k), esc(a), esc(z)) for k, a, z in items)
    return '<div class="kpirow" data-reveal>\n%s</div>\n' % cells


# ══════════════════════════════════════════════════ ことばを見せる

def quote(text, who=None, role=None):
    """引用。明朝の大きな引用符を背に置く。

    `take`（おざけんの一言）とは別物。**こちらは他人の言葉**で、
    出典を示して引く。take は2つまでという制限があるが、
    こちらは資料の中でいくつ置いてもよい。
    """
    foot = ''
    if who:
        foot = ('  <p class="qt-w"><b>%s</b>%s</p>\n'
                % (esc(who), '<span>%s</span>' % esc(role) if role else ''))
    return ('<figure class="quote" data-reveal>\n'
            '  <blockquote class="qt-t">%s</blockquote>\n%s</figure>\n'
            % (text, foot))


def lead_reveal(lines, accent=None):
    """大きな一文を、行ごとに下から立ち上げる。

    **行そのものを窓にして、中身を下から出す。**
    行の外に出たものは、はみ出すのではなく単に見えない。
    accent に渡した行番号（0始まり）だけ、赤で出す。
    """
    acc = set(accent or [])
    rows = ''.join(
        '  <span class="lr-row"><span style="--i:%d"%s>%s</span></span>\n'
        % (i, ' class="lr-a"' if i in acc else '', esc(t))
        for i, t in enumerate(lines))
    return '<div class="leadreveal" data-reveal>\n%s</div>\n' % rows


def callout(kind, title, text):
    """囲み。kind は point（要点）/ warn（落とし穴）/ note（補足）。

    **3種類しか用意しない。** 種類を増やすと、書く側が毎回迷い、
    読む側は色の意味を覚えられない。
    """
    icon = {'point': '要点', 'warn': '落とし穴', 'note': '補足'}.get(kind, '要点')
    return ('<div class="callout co-%s" data-reveal>\n'
            '  <span class="co-k">%s</span>\n'
            '  <div class="co-b"><p class="co-t">%s</p><p class="co-x">%s</p></div>\n'
            '</div>\n' % (kind, esc(icon), esc(title), text))


def terms(items):
    """用語の定義。items: [(語, 読み・英字, 説明)]。

    講演では、聴いている人の語彙が揃っていない。
    **その場で1行の説明を添える**ための部品。
    """
    rows = ''.join(
        '  <div class="tm-i"><div class="tm-h"><b>%s</b>%s</div><p>%s</p></div>\n'
        % (esc(w), '<span>%s</span>' % esc(r) if r else '', esc(d))
        for w, r, d in items)
    return '<div class="terms" data-reveal>\n%s</div>\n' % rows


# ══════════════════════════════════════════════════ 流れと構造

def steps(items, note=None):
    """縦に積む手順。items: [(見出し, 説明)]。

    横に流す `fig_flow` と使い分ける。**手順が5つを超えるとき**と、
    **各手順の説明が長いとき**は、こちらの縦に置く。
    """
    rows = ''.join(
        '  <div class="st-i" style="--i:%d"><span class="st-n">%02d</span>'
        '<div class="st-b"><p class="st-t">%s</p><p class="st-x">%s</p></div></div>\n'
        % (i, i + 1, esc(h), x) for i, (h, x) in enumerate(items))
    return ('<div class="steps" data-reveal>\n%s%s</div>\n'
            % (rows, '  <p class="st-note">%s</p>\n' % esc(note) if note else ''))


def timeline(items):
    """時系列。items: [(いつ, 何が, 説明)]。

    `fig_timeline` は横に流す図版。こちらは本文の部品で、
    **件数が多いとき**と、**説明が長いとき**に縦で置く。
    """
    rows = ''.join(
        '  <div class="tl-i" style="--i:%d"><span class="tl-d">%s</span>'
        '<div class="tl-b"><p class="tl-t">%s</p><p class="tl-x">%s</p></div></div>\n'
        % (i, esc(d), esc(t), x) for i, (d, t, x) in enumerate(items))
    return '<div class="tline" data-reveal>\n%s</div>\n' % rows


def phases(items):
    """横に並ぶ段階。items: [(番号や期間, 見出し, 一言)]。3〜5個。

    帯が左から順に満ちる。「いまどの段階か」ではなく
    「全体が何段階か」を見せるための部品。
    """
    cells = ''.join(
        '  <div class="ph-i" style="--i:%d"><span class="ph-n">%s</span>'
        '<p class="ph-t">%s</p><p class="ph-x">%s</p>'
        '<span class="ph-bar" aria-hidden="true"><i></i></span></div>\n'
        % (i, esc(n), esc(t), esc(x)) for i, (n, t, x) in enumerate(items))
    return '<div class="phases" data-reveal>\n%s</div>\n' % cells


def split(left_title, left_body, right_title, right_body, label=None):
    """左右に分ける。対比というより「二つの側面」を並べるとき。

    `fig_versus` は赤い側が「注意すべき方」という約束があるので、
    **優劣の無い2つ**を並べたいときはこちらを使う。
    """
    lb = '  <span class="sp-lb">%s</span>\n' % esc(label) if label else ''
    return ('<div class="split" data-reveal>\n%s'
            '  <div class="sp-h"><p class="sp-t">%s</p>%s</div>\n'
            '  <div class="sp-h"><p class="sp-t">%s</p>%s</div>\n'
            '</div>\n' % (lb, esc(left_title), left_body,
                          esc(right_title), right_body))


# ══════════════════════════════════════════════════ 一覧と演出

def checklist(items, note=None):
    """チェックの一覧。items: [(True/False, 文)]。

    印は線を2本、角度をつけて引いて作る。**丸の中に✓の字を置かない。**
    書体によって形が変わるうえ、投影すると潰れる。
    """
    rows = ''.join(
        '  <div class="ck-i %s" style="--i:%d">'
        '<span class="ck-m" aria-hidden="true"><i></i><i></i></span>'
        '<p>%s</p></div>\n'
        % ('is-y' if ok else 'is-n', i, t) for i, (ok, t) in enumerate(items))
    return ('<div class="checks" data-reveal>\n%s%s</div>\n'
            % (rows, '  <p class="ck-note">%s</p>\n' % esc(note) if note else ''))


def faq(items):
    """問いと答え。items: [(問い, 答え)]。

    **開閉させない。** 投影中に開く手間は取れないし、
    閉じている答えは会場の後ろからは存在しないのと同じ。

    **文は必ず <p> で包んでから並べる。** 包まずに display:grid の
    直下へ置くと、中の <b> までがそれぞれ独立した項目になり、
    答えが1文字ずつ縦に並ぶ（実際にそうなった）。
    """
    rows = ''.join(
        '  <div class="fq-i" style="--i:%d">'
        '<div class="fq-q"><span class="fq-m">Q</span><p>%s</p></div>'
        '<div class="fq-a"><span class="fq-m">A</span><p>%s</p></div></div>\n'
        % (i, esc(q), a) for i, (q, a) in enumerate(items))
    return '<div class="faq" data-reveal>\n%s</div>\n' % rows


def marquee(items, label=None):
    """語を横に流し続ける帯。列挙が長くて、全部は読ませなくてよいとき。

    **同じ列を2つ並べて、片方が出ていくあいだにもう片方が入る。**
    1列だと、末尾が抜けたあとに空白が横切る。
    """
    one = ''.join('<span>%s</span>' % esc(t) for t in items)
    lb = '  <span class="mq-lb">%s</span>\n' % esc(label) if label else ''
    return ('<div class="marquee" data-reveal>\n%s'
            '  <div class="mq-w"><div class="mq-t" aria-hidden="true">%s%s</div></div>\n'
            '</div>\n' % (lb, one, one))


def spotlight(title, text, meta=None):
    """光がゆっくり横切る、濃い面のカード。節の締めに1つだけ置く。

    **1つの面に2つ置かない。** 光が2箇所で走ると、
    目がどちらを追えばよいのか決められなくなる。
    """
    m = '  <p class="sl-m">%s</p>\n' % esc(meta) if meta else ''
    return ('<div class="spotlight" data-reveal>\n'
            '  <p class="sl-t">%s</p>\n  <p class="sl-x">%s</p>\n%s</div>\n'
            % (esc(title), text, m))


def wave(label=None, n=9):
    """縦棒が波打つ印。音・処理・稼働の「動いている」を示す小さな部品。

    **周期は互いに割り切れない秒数にしてある。** 割り切れると
    数秒ごとに全部が整列し直して、作り物だと分かってしまう。
    """
    bars = ''.join('<i style="--d:%s;--g:%s"></i>'
                   % (('%.2f' % (0.74 + (i % 5) * 0.19)),
                      ('-%.2f' % (0.13 * i)))
                   for i in range(n))
    lb = '<span class="wv-lb">%s</span>' % esc(label) if label else ''
    return ('<div class="wave" data-reveal>'
            '<span class="wv-b" aria-hidden="true">%s</span>%s</div>\n'
            % (bars, lb))
