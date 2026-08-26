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

── 押せる部品について ──────────────────────────────────

**常時の動きは足さない。触れたときだけ返す。**
投影中に動くものが増えると、本文が読めなくなる。だから
下の7つは、指かマウスが触れるまで完全に止まっている。

押されることが本当に起きるのは、**講演のあとに渡したURLを
参加者が自分の端末で開いたとき**。そこで効くものだけを置いた。
`copyable`（依頼文をその場でコピー）と `flip`（考えてから開く）が
その代表で、どちらも紙の資料では成立しない。

押した感触は ripple ひとつに統一してある。部品ごとに違う
返し方をすると、押せるものと押せないものの区別が学習できない。
JSは tpl_tail.html にあり、**document への委譲で動く**ので、
暗号化された本文が後から差し込まれても効く。
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


# ══════════════════════════════════════════════════ 押せる部品
#
# **どれも、触れるまでは完全に止まっている。**
# 投影中に動くものが増えると本文が読めなくなるので、
# 常時のアニメーションはここには置かない。

def copyable(text, label='この依頼文をコピー', note=None):
    """押すと、中の文をクリップボードに写す。

    **紙の資料では成立しない部品。** 講演のあとにURLを渡すと、
    参加者はその場で依頼文を自分のAIに貼れる。
    プロンプトの例・設定値・コマンドを載せるときに使う。

    改行を含めたいときは text に \n を入れる（そのまま写る）。
    """
    return ('<div class="copyable" data-reveal>\n'
            '  <pre class="cp-t">%s</pre>\n'
            '  <button class="cp-b oz-press" type="button" data-copy>'
            '<span class="cp-i" aria-hidden="true"></span>%s</button>\n%s</div>\n'
            % (esc(text), esc(label),
               '  <p class="cp-n">%s</p>\n' % esc(note) if note else ''))


def flip(front, back, hint='押すと、答えが出ます'):
    """押すと裏返る。表に問い、裏に答えを置く。

    **講演で「どう思いますか」と投げてから開くための部品。**
    先に答えが見えていると、聴いている人は考えない。

    表と裏は同じ升目に重ねてある（grid-area を揃える）。
    位置合わせに絶対配置を使うと、片方の高さが変わったときに崩れる。
    """
    return ('<div class="flip oz-press" data-flip data-reveal tabindex="0" role="button">\n'
            '  <div class="fl-in">\n'
            '    <div class="fl-f"><p>%s</p><span class="fl-h">%s</span></div>\n'
            '    <div class="fl-b"><p>%s</p></div>\n'
            '  </div>\n</div>\n' % (front, esc(hint), back))


def toggle_pair(a_label, a_body, b_label, b_body, label=None):
    """2つを1枚の場所で切り替える。Before / After に。

    横に並べる `split` と違い、**同じ場所で入れ替わる**ので
    差分そのものが見える。並べると目が左右に動いて、
    どこが変わったのかを自分で探すことになる。
    """
    lb = '  <span class="tg-lb">%s</span>\n' % esc(label) if label else ''
    return ('<div class="togglepair" data-toggle data-reveal>\n%s'
            '  <div class="tg-sw" role="tablist">'
            '<button class="tg-k oz-press is-on" type="button" role="tab">%s</button>'
            '<button class="tg-k oz-press" type="button" role="tab">%s</button>'
            '<span class="tg-ink" aria-hidden="true"></span></div>\n'
            '  <div class="tg-st"><div class="tg-p is-on">%s</div>'
            '<div class="tg-p">%s</div></div>\n</div>\n'
            % (lb, esc(a_label), esc(b_label), a_body, b_body))


def tabs(items):
    """立場ごとに中身を切り替える。items: [(見出し, 中身)]。2〜4個。

    **1つの面で、3倍の内容を持てる。** 経営・現場・情シスのように
    聞き手によって刺さる話が違うとき、その場で切り替えて見せられる。
    下の線が押した札へ滑って移る。
    """
    keys = ''.join(
        '<button class="tb-k oz-press%s" type="button" role="tab">%s</button>'
        % (' is-on' if i == 0 else '', esc(t)) for i, (t, _) in enumerate(items))
    panes = ''.join(
        '<div class="tb-p%s">%s</div>' % (' is-on' if i == 0 else '', b)
        for i, (_, b) in enumerate(items))
    return ('<div class="tabs" data-tabs data-reveal>\n'
            '  <div class="tb-ks" role="tablist">%s'
            '<span class="tb-ink" aria-hidden="true"></span></div>\n'
            '  <div class="tb-st">%s</div>\n</div>\n' % (keys, panes))


def accordion(items, note=None):
    """押すと開く一覧。items: [(見出し, 中身)]。

    **投影では使わない。** 閉じている中身は、会場の後ろからは
    存在しないのと同じ。これは**渡したあとに読む人**のための部品で、
    参照用の長い一覧（施策・用語・FAQの詳細）を畳んでおくときに使う。
    投影して話す内容なら `faq` か `steps` を使う。
    """
    rows = ''.join(
        '  <div class="ac-i"><button class="ac-h oz-press" type="button" '
        'aria-expanded="false">%s<span class="ac-x" aria-hidden="true"></span></button>'
        '<div class="ac-b"><div class="ac-c">%s</div></div></div>\n'
        % (esc(h), b) for h, b in items)
    return ('<div class="accordion" data-acc data-reveal>\n%s%s</div>\n'
            % (rows, '  <p class="ac-n">%s</p>\n' % esc(note) if note else ''))


def counter(items, note=None):
    """数字が、0から回って止まる。items: [(数値, 単位, 何の数字か)]。

    `statgrid` は置いた瞬間から数字が見えている。こちらは
    **画面に入ってから回る**ので、数の大きさが時間として伝わる。
    押すともう一度回るので、講演で「もう一度見せて」に応えられる。

    数値は整数で渡す（回すために数として扱う）。
    """
    cells = ''.join(
        '  <div class="ct-i"><div class="ct-v">'
        '<b data-to="%d">0</b><i>%s</i></div><p>%s</p></div>\n'
        % (int(v), esc(u), esc(l)) for v, u, l in items)
    return ('<div class="counter oz-press" data-count data-reveal>\n%s%s</div>\n'
            % (cells, '  <p class="ct-n">%s</p>\n' % esc(note) if note else ''))


def poll(question, options, answer, why=None):
    """選ばせてから、正解を返す。options: [文, ...]、answer は 0 始まりの番号。

    **確認テスト（quiz）との違いは、置き場所と目的。**
    quiz は隠しコマンドで開く、裏資料限定の理解度チェック。
    こちらは本文に置いて、**その場の1問**で聴衆の手を動かす。
    表の資料にも置ける。
    """
    opts = ''.join(
        '<button class="pl-o oz-press" type="button" data-i="%d">'
        '<span class="pl-m" aria-hidden="true"></span>%s</button>' % (i, esc(o))
        for i, o in enumerate(options))
    w = '  <p class="pl-w">%s</p>\n' % why if why else ''
    return ('<div class="poll" data-poll data-a="%d" data-reveal>\n'
            '  <p class="pl-q">%s</p>\n  <div class="pl-os">%s</div>\n%s</div>\n'
            % (int(answer), esc(question), opts, w))
