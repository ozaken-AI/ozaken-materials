#!/usr/bin/env python3
"""資料マトリクスのページを組む。

**まず答えるのは「テーマを網羅できているか」。**

前の版は 資料 × 概念 の格子をいきなり出していた。87行 × 45列で、
列見出しは回転した縦書き。ほとんどの升は空なので、目に入るのは
まばらな点の海だけで、どのテーマが厚くてどこが手薄なのかは読めなかった。
格子は「2本の資料が同じ概念を厚く扱っていないか」を確かめる道具としては
正しいが、それは網羅性を見たあとに使う道具で、最初に出すものではない。

そこで並べ替えた。

  1. 手薄なところ    ── 正典が無い／触れる資料が少ない概念を、先に名指しする
  2. テーマ別の網羅性 ── 群ごとに概念カード。正典・本数・厚みを1枚で
  3. 孤立している資料 ── どの概念にも触れていない資料
  4. 近い2本        ── 同じ概念を厚く扱う組。主張を揃える対象
  5. 全格子         ── 折りたたみ。細かく突き合わせたいときだけ開く

ページ自体は資料ではないので、ozaken-web-style の規約（奇数セクション等）は
適用しない。パスワード台帳と同じ、道具としてのページ。
"""
import html as H
import os
import zlib

from crossref_data import CONCEPTS, GROUPS

# セルの濃さ。言及回数で3段
HEAVY = 8

# 網羅の段。触れている資料の本数で分ける
#   正典が1本あるだけの概念は「その概念を説明した資料はあるが、
#   ほかの資料がそこへ寄っていない」状態で、いちばん食い違いが出やすい
THIN, FAIR = 3, 9


def _cell(rel, name, n, canon):
    if rel == canon:
        return ('<td class="v v4" title="正典">◎</td>', 4)
    if not n:
        return ('<td class="v v0"></td>', 0)
    if n >= HEAVY:
        return ('<td class="v v3" title="%d回">●</td>' % n, 3)
    if n >= 3:
        return ('<td class="v v2" title="%d回">●</td>' % n, 2)
    return ('<td class="v v1" title="%d回">・</td>' % n, 1)


def _slug(name):
    """概念名から、飛び先にできる短い印を作る。

    日本語をそのまま id にすると参照側で壊れる。
    hash() は実行ごとに値が変わるので、毎回ちがう id が出て差分が濁る。
    内容だけで決まる crc32 を使う。
    """
    return '%08x' % (zlib.crc32(name.encode('utf-8')) & 0xffffffff)


def _rank(touch, heavy, has_canon):
    """網羅の段を決める。正典が無いものは、本数にかかわらず最優先で拾う"""
    if not has_canon:
        return ('nocanon', '正典なし')
    if touch == 0:
        return ('empty', '正典だけ')
    if touch <= THIN:
        return ('thin', '手薄')
    if touch <= FAIR:
        return ('fair', 'ふつう')
    return ('rich', '厚い')


def build(rows, edges, stamp):
    """rows: [(rel, title, {概念名: 回数}), ...] / edges: [(a, b, w), ...]"""
    names = [n for _, ns in GROUPS for n in ns if n in CONCEPTS]
    names += [n for n in CONCEPTS if n not in names]      # 群に載せ忘れた分
    have = {rel for rel, _, _ in rows}
    title_of = {rel: t for rel, t, _ in rows}

    # ── 概念ごとに集計する。網羅性はここから全部出る ──
    agg = {}
    for n in names:
        canon = CONCEPTS[n][0]
        touch = heavy = 0
        for rel, _, hits in rows:
            if rel == canon:
                continue                                   # 正典は本数に数えない
            k = hits.get(n, 0)
            if k:
                touch += 1
            if k >= HEAVY:
                heavy += 1
        agg[n] = (canon, canon in have, touch, heavy)

    maxtouch = max([a[2] for a in agg.values()] + [1])

    # ── 1. 手薄なところ。名前だけ1行に並べる ──
    #    ここでカードにすると、下の一覧と同じ概念をもう一度読むことになる
    todo = []
    for n in names:
        canon, ok, touch, heavy = agg[n]
        key, label = _rank(touch, heavy, ok)
        if key in ('nocanon', 'empty', 'thin'):
            todo.append('<a class="chip k-%s" href="#c-%s">%s<b>%s</b></a>'
                        % (key, _slug(n), H.escape(n),
                           '正典なし' if key == 'nocanon' else
                           '0本' if key == 'empty' else '%d本' % touch))
    todo_html = ('<div class="chips">%s</div>' % ''.join(todo)) if todo else \
        '<p class="none">手薄な概念はありません。どのテーマにも正典があり、'\
        '複数の資料がそこへ寄っています。</p>'

    # ── 2. テーマ別の網羅性。**カードではなく、起点のそろった表にする** ──
    #    カードを格子に並べると、帯の左端が揃わないので概念どうしを比べられない。
    #    網羅性を見るページで比べられないのは致命的なので、1行1概念の表にした。
    #    群の中は本数の少ない順。手薄なものが自然に上へ来る
    blocks = []
    for g, ns in GROUPS:
        ns = [n for n in ns if n in CONCEPTS]
        if not ns:
            continue
        ns = sorted(ns, key=lambda n: (agg[n][1], agg[n][2], agg[n][3]))
        lines = []
        for n in ns:
            canon, ok, touch, heavy = agg[n]
            key, label = _rank(touch, heavy, ok)
            w = int(touch * 100 / maxtouch)
            wh = int(heavy * 100 / maxtouch)
            canon_html = ('<a href="%s">%s</a>'
                          % (H.escape(canon), H.escape(title_of.get(canon, canon)))
                          if ok else '<span class="ng">正典が見つかりません</span>')
            lines.append(
                '<tr class="k-%s" id="c-%s">'
                '<td class="st"><span>%s</span></td>'
                '<td class="nm"><b>%s</b><em>%s</em></td>'
                '<td class="cn">%s</td>'
                '<td class="bw"><span class="bb"><i style="width:%d%%"></i>'
                '<u style="width:%d%%"></u></span></td>'
                '<td class="n1">%d</td><td class="n2">%d</td></tr>'
                % (key, _slug(n), H.escape(label), H.escape(n),
                   H.escape(CONCEPTS[n][2]), canon_html, w, wh, touch, heavy))
        blocks.append(
            '<h3 class="gh">%s<span>%d の概念</span></h3>'
            '<table class="cov"><thead><tr>'
            '<th class="st">状態</th><th class="nm">概念</th><th class="cn">正典</th>'
            '<th class="bw">触れている資料</th><th class="n1">触れる</th>'
            '<th class="n2">厚く</th></tr></thead><tbody>%s</tbody></table>'
            % (H.escape(g), len(ns), ''.join(lines)))

    # ── 格子（詳細）。ここは前の版のまま ──
    head1, head2 = [], []
    for g, ns in GROUPS:
        ns = [n for n in ns if n in CONCEPTS]
        if ns:
            head1.append('<th class="g" colspan="%d"><span>%s</span></th>'
                         % (len(ns), H.escape(g)))
    for n in names:
        canon = CONCEPTS[n][0]
        head2.append('<th class="c"><a href="%s" title="正典: %s"><span>%s</span></a></th>'
                     % (H.escape(canon), H.escape(canon), H.escape(n)))

    body, cur, alone = [], None, []
    for rel, title, hits in rows:
        d = os.path.dirname(rel) or 'そのほか'
        if d != cur:
            cur = d
            body.append('<tr class="grp"><th colspan="%d">%s</th></tr>'
                        % (len(names) + 2, H.escape(d)))
        cells, score, mine = [], 0, 0
        for n in names:
            td, lv = _cell(rel, n, hits.get(n, 0), CONCEPTS[n][0])
            cells.append(td)
            if lv == 4:
                mine += 1
            elif lv:
                score += 1
        if not score and not mine:
            alone.append((rel, title))
        body.append(
            '<tr data-n="%d"><th class="r"><a href="%s"><span class="t">%s</span>'
            '<span class="p">%s</span></a></th>%s'
            '<td class="sum">%s</td></tr>'
            % (score + mine, H.escape(rel), H.escape(title), H.escape(rel),
               ''.join(cells),
               ('<b title="正典である概念">◎%d</b>' % mine if mine else '')
               + ('<i title="触れている概念">%d</i>' % score if score else '')))

    ed = []
    for a, b, w, ta, tb in edges[:24]:
        ed.append('<li><span class="w">%d</span>'
                  '<a href="%s">%s</a><span class="x">↔</span><a href="%s">%s</a></li>'
                  % (w, H.escape(a), H.escape(ta), H.escape(b), H.escape(tb)))

    orphan = ('<ul class="orphan">%s</ul>'
              % ''.join('<li><a href="%s">%s</a></li>' % (H.escape(r), H.escape(t))
                        for r, t in alone)) if alone else \
             '<p class="none">すべての資料が、どこかの概念でつながっています。</p>'

    nissue = len(todo)
    out = TEMPLATE
    for k, v in (('__HEAD1__', ''.join(head1)), ('__HEAD2__', ''.join(head2)),
                 ('__BODY__', '\n'.join(body)), ('__EDGES__', ''.join(ed)),
                 ('__ORPHAN__', orphan), ('__TODO__', todo_html),
                 ('__GROUPS__', ''.join(blocks)),
                 ('__NDOC__', str(len(rows))), ('__NCON__', str(len(names))),
                 ('__NISSUE__', str(nissue)), ('__NALONE__', str(len(alone))),
                 ('__NEDGE__', str(len(edges))), ('__STAMP__', stamp)):
        out = out.replace(k, v)
    return out


TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>資料マトリクス | おざけん</title>
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;600;700&family=Shippori+Mincho+B1:wght@500;600&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root{--navy:#1f3864;--navy-deep:#141d35;--azure:#2e5496;--azure-pale:#d8e4f0;
  --red:#e23744;--red-bright:#ff5d6a;--muted:#6b7a99;--amber:#c9762f;--teal:#2f8f8a;
  --fs:'Zen Kaku Gothic New',sans-serif;--fm:'Shippori Mincho B1',serif;--fe:'Hanken Grotesk',sans-serif}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{background:var(--navy-deep)}
body{font-family:var(--fs);color:#fff;line-height:1.8;
  background:radial-gradient(ellipse 70% 50% at 50% -6%,rgba(46,84,150,.55),transparent 62%),
    linear-gradient(168deg,#1f3864 0%,#182a52 44%,#141d35 100%);
  background-attachment:fixed;min-height:100vh;padding:clamp(1.6rem,5vh,3rem) clamp(.8rem,3vw,1.6rem)}
.wrap{width:min(1500px,100%);margin:0 auto}
.badge{display:inline-flex;align-items:center;gap:.5rem;padding:.45em .9em;border-radius:999px;
  background:rgba(20,29,53,.5);border:1px solid rgba(216,228,240,.22);
  font-family:var(--fe);font-size:.62rem;font-weight:600;letter-spacing:.16em;
  color:rgba(216,228,240,.9);margin-bottom:1.2rem}
.badge .dot{width:6px;height:6px;border-radius:50%;background:var(--red-bright);
  box-shadow:0 0 8px var(--red-bright);animation:bl 2.4s ease-in-out infinite}
@keyframes bl{0%,100%{opacity:1}50%{opacity:.35}}
.badge .ja{font-family:var(--fs);letter-spacing:.06em;font-size:.66rem;color:#fff}
h1{font-family:var(--fm);font-weight:600;font-size:clamp(1.6rem,4.6vw,2.2rem);margin-bottom:.5rem}
.lead{font-size:.86rem;color:rgba(216,228,240,.75);margin-bottom:1.4rem;max-width:64ch}
h2{font-family:var(--fm);font-weight:600;font-size:1.12rem;margin:2.6rem 0 .5rem}
h2 em{font-style:normal;font-family:var(--fe);font-size:.7rem;font-weight:700;
  letter-spacing:.14em;color:rgba(159,198,245,.8);display:block;margin-bottom:.1rem}
.note{font-size:.78rem;color:rgba(216,228,240,.62);margin-bottom:1rem;max-width:64ch}
.stats{display:flex;flex-wrap:wrap;gap:.7rem;margin-bottom:1.2rem}
.stat{flex:1;min-width:120px;padding:.8rem 1rem;border-radius:12px;
  background:rgba(255,255,255,.06);border:1px solid rgba(216,228,240,.16)}
.stat b{display:block;font-family:var(--fe);font-size:1.6rem;font-weight:700;line-height:1.2}
.stat span{font-size:.72rem;color:rgba(216,228,240,.7)}
.stat.warn{border-color:rgba(255,93,106,.5);background:rgba(226,55,68,.12)}
.stat.warn b{color:var(--red-bright)}

/* ── 手薄なところ。カードにすると下の表と二度読みになるので、名前だけ並べる ── */
.chips{display:flex;flex-wrap:wrap;gap:.4rem}
.chips .chip{display:inline-flex;align-items:baseline;gap:.45em;
  padding:.34em .8em;border-radius:999px;font-size:.82rem;text-decoration:none;
  background:rgba(255,255,255,.06);border:1px solid rgba(216,228,240,.2);color:#fff}
.chips .chip b{font-family:var(--fe);font-size:.62rem;font-weight:700;letter-spacing:.06em;
  color:rgba(216,228,240,.6)}
.chips .chip:hover{border-color:var(--red-bright)}
.chips .chip.k-nocanon{border-color:rgba(255,93,106,.65);background:rgba(226,55,68,.16)}
.chips .chip.k-nocanon b{color:var(--red-bright)}
.chips .chip.k-empty{border-color:rgba(201,118,47,.6);background:rgba(201,118,47,.14)}

/* ── テーマ別の網羅性 ── */
.gh{font-size:.95rem;font-weight:700;margin:2rem 0 .5rem;
  display:flex;align-items:baseline;gap:.8rem}
.gh span{font-family:var(--fe);font-size:.64rem;font-weight:600;letter-spacing:.1em;
  color:rgba(216,228,240,.5)}
table.cov{width:100%;border-collapse:collapse;font-size:.84rem}
table.cov thead th{font-family:var(--fe);font-size:.6rem;font-weight:700;
  letter-spacing:.12em;color:rgba(216,228,240,.45);text-align:left;
  padding:.2rem .7rem .45rem;border-bottom:1px solid rgba(216,228,240,.16);
  white-space:nowrap}
table.cov tbody tr{border-bottom:1px solid rgba(216,228,240,.08)}
table.cov tbody tr:hover{background:rgba(255,255,255,.045)}
table.cov td{padding:.6rem .7rem;vertical-align:middle}
/* 状態は左端の色帯で示す。ここが揃っていると、上から下へ目で追える */
td.st{width:76px;padding-left:0}
td.st span{display:inline-block;width:100%;text-align:center;
  font-size:.68rem;font-weight:700;padding:.2em 0;border-radius:5px;
  background:rgba(255,255,255,.08);color:rgba(216,228,240,.8)}
tr.k-rich td.st span{background:rgba(47,143,138,.3);color:#7fd6d0}
tr.k-fair td.st span{background:rgba(159,198,245,.2);color:#bcd7f6}
tr.k-thin td.st span{background:rgba(201,118,47,.3);color:#eab27a}
tr.k-empty td.st span{background:rgba(201,118,47,.42);color:#f2c795}
tr.k-nocanon td.st span{background:rgba(226,55,68,.42);color:#ffc2c7}
td.nm{width:23%;min-width:150px}
td.nm b{display:block;font-size:.9rem;font-weight:700;line-height:1.5}
td.nm em{display:block;font-style:normal;font-size:.7rem;line-height:1.5;
  color:rgba(216,228,240,.5)}
td.cn{width:28%;min-width:170px;font-size:.78rem;line-height:1.5}
td.cn a{color:#9fc6f5;text-decoration:none;display:block;overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}
td.cn a:hover{color:#fff;text-decoration:underline}
td.cn .ng{color:var(--red-bright);font-weight:700}
/* **帯の左端をそろえる。** カードを並べていたときは起点がばらばらで、
   概念どうしの多い少ないが目で比べられなかった */
td.bw{min-width:130px}
.bb{position:relative;display:block;height:9px;border-radius:5px;
  background:rgba(255,255,255,.08);overflow:hidden}
.bb i,.bb u{position:absolute;left:0;top:0;height:100%;border-radius:5px}
.bb i{background:rgba(159,198,245,.6)}
.bb u{background:var(--red-bright);opacity:.9}
td.n1,td.n2{width:52px;text-align:right;font-family:var(--fe);font-size:.86rem;
  font-weight:700}
td.n1{color:#bcd7f6}
td.n2{color:var(--red-bright)}
tr.k-empty td.n1,tr.k-nocanon td.n1{color:rgba(216,228,240,.35)}
@media(max-width:760px){
  td.cn,th.cn{display:none}
  td.nm em{display:none}
}

/* ── 詳細（折りたたみ） ── */
details.more{margin-top:2.2rem;border-radius:14px;border:1px solid rgba(216,228,240,.16);
  background:rgba(10,15,28,.35);padding:.2rem .2rem}
details.more>summary{cursor:pointer;padding:.9rem 1.1rem;font-size:.88rem;font-weight:700;
  list-style:none;display:flex;align-items:center;gap:.6rem}
details.more>summary::-webkit-details-marker{display:none}
details.more>summary::before{content:'▸';color:var(--red-bright);font-size:.8rem}
details.more[open]>summary::before{content:'▾'}
details.more>summary em{font-style:normal;font-weight:400;font-size:.74rem;
  color:rgba(216,228,240,.6)}
.inner{padding:0 1.1rem 1.1rem}
.bar{display:flex;flex-wrap:wrap;align-items:center;gap:.6rem 1.1rem;margin-bottom:.9rem}
#q{flex:1;min-width:180px;max-width:320px;padding:.5rem .9rem;border-radius:999px;
  background:rgba(255,255,255,.08);border:1px solid rgba(216,228,240,.24);
  color:#fff;font-family:var(--fs);font-size:.82rem}
#q::placeholder{color:rgba(216,228,240,.45)}
#q:focus{outline:none;border-color:var(--red-bright)}
.legend{display:flex;flex-wrap:wrap;gap:.2rem 1rem;font-size:.72rem;color:rgba(216,228,240,.7)}
.legend i{font-style:normal;font-family:var(--fe);margin-right:.3em}
.legend .k4{color:var(--red-bright)}.legend .k3{color:#9fc6f5}
.legend .k2{color:rgba(159,198,245,.65)}.legend .k1{color:rgba(216,228,240,.42)}
button.rst{padding:.35rem .8rem;border-radius:999px;cursor:pointer;font-family:var(--fs);
  font-size:.72rem;color:rgba(216,228,240,.8);background:rgba(255,255,255,.06);
  border:1px solid rgba(216,228,240,.2)}
button.rst:hover{border-color:var(--red-bright);color:#fff}
.scroll{overflow:auto;max-height:74vh;border-radius:14px;
  border:1px solid rgba(216,228,240,.16);background:rgba(10,15,28,.42)}
table.mx{width:100%;border-collapse:separate;border-spacing:0;font-size:.78rem}
table.mx th,table.mx td{border-bottom:1px solid rgba(216,228,240,.09)}
table.mx thead th{position:sticky;background:#182a52;z-index:2}
table.mx thead tr:first-child th{top:0;height:26px}
table.mx thead tr:nth-child(2) th{top:26px}
th.g{font-family:var(--fe);font-size:.6rem;font-weight:700;letter-spacing:.12em;
  color:rgba(159,198,245,.85);border-left:1px solid rgba(216,228,240,.16);
  border-bottom:1px solid rgba(216,228,240,.2)}
th.g span{font-family:var(--fs);letter-spacing:.06em}
/* 縦書き（writing-mode）は字体の縦メトリクスに頼るので、
   書体が読み込めない環境だと漢字が重なって潰れる。回転なら字体に依存しない */
th.c{width:26px;min-width:26px;max-width:26px;height:200px;padding:0;
  border-bottom:1px solid rgba(216,228,240,.24)}
th.c a{position:absolute;left:50%;bottom:10px;display:block;white-space:nowrap;
  transform:rotate(-90deg);transform-origin:left bottom;margin-left:.1em;
  font-size:.7rem;font-weight:500;line-height:1;
  color:rgba(216,228,240,.82);text-decoration:none}
th.c a:hover{color:#fff}
th.r{position:sticky;left:0;z-index:1;background:#16233f;text-align:left;
  padding:.5rem .7rem;min-width:300px;max-width:300px}
th.r a{color:#fff;text-decoration:none;display:block}
th.r a:hover .t{color:var(--red-bright)}
th.r .t{display:block;font-size:.78rem;font-weight:500;line-height:1.45;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
th.r .p{display:block;font-family:var(--fe);font-size:.6rem;
  color:rgba(216,228,240,.45);letter-spacing:.02em}
tr.grp th{position:sticky;left:0;background:#1b2b4d;font-family:var(--fe);
  font-size:.62rem;font-weight:700;letter-spacing:.14em;
  color:rgba(159,198,245,.9);padding:.35rem .7rem;text-align:left}
td.v{text-align:center;font-size:.72rem;line-height:1}
td.v0{color:transparent}
td.v1{color:rgba(216,228,240,.34)}
td.v2{color:rgba(159,198,245,.7)}
td.v3{color:#9fc6f5;font-size:.86rem}
td.v4{color:var(--red-bright);font-size:.9rem}
tbody tr:hover td.v0{background:rgba(255,255,255,.03)}
tbody tr:hover th.r{background:#1d2c4c}
td.sum{white-space:nowrap;padding:0 .6rem;font-family:var(--fe);font-size:.66rem;
  color:rgba(216,228,240,.55);text-align:right}
td.sum b{color:var(--red-bright);margin-right:.4em}
td.sum i{font-style:normal}
tr.hide{display:none}

ul.orphan,ul.edges{list-style:none;display:grid;gap:.35rem;
  grid-template-columns:repeat(auto-fill,minmax(300px,1fr))}
ul.orphan li,ul.edges li{padding:.5rem .8rem;border-radius:9px;font-size:.78rem;
  background:rgba(255,255,255,.05);border:1px solid rgba(216,228,240,.14)}
ul.orphan a,ul.edges a{color:#9fc6f5;text-decoration:none}
ul.orphan a:hover,ul.edges a:hover{color:#fff;text-decoration:underline}
ul.edges .w{font-family:var(--fe);font-size:.64rem;font-weight:700;color:var(--red-bright);
  margin-right:.5em}
ul.edges .x{color:rgba(216,228,240,.4);margin:0 .4em}
.none{font-size:.8rem;color:rgba(216,228,240,.6)}
footer{margin-top:2.6rem;padding-top:1.2rem;border-top:1px solid rgba(216,228,240,.14);
  font-family:var(--fe);font-size:.66rem;letter-spacing:.1em;color:rgba(216,228,240,.5);
  display:flex;justify-content:space-between;flex-wrap:wrap;gap:.5rem}
footer a{color:rgba(216,228,240,.7);text-decoration:none}
footer a:hover{color:#fff}
@media(max-width:720px){th.r{min-width:190px;max-width:190px}}
</style>
</head>
<body>
<div class="wrap">
  <span class="badge"><span class="dot"></span>
    <span class="ja">おざけん コンテンツ管理システム</span> / MATRIX</span>
  <h1>資料マトリクス</h1>
  <p class="lead">テーマを網羅できているかを見るページです。
    概念ごとに<b>正典が決まっているか</b>と<b>何本の資料がそこへ寄っているか</b>を並べています。
    触れる資料が少ない概念は、説明が食い違っても気づけません。最終更新 __STAMP__</p>

  <div class="stats">
    <div class="stat"><b>__NDOC__</b><span>資料</span></div>
    <div class="stat"><b>__NCON__</b><span>概念</span></div>
    <div class="stat warn"><b>__NISSUE__</b><span>手薄な概念</span></div>
    <div class="stat warn"><b>__NALONE__</b><span>孤立している資料</span></div>
    <div class="stat"><b>__NEDGE__</b><span>資料どうしのつながり</span></div>
  </div>

  <h2><em>GAPS</em>手薄なところ</h2>
  <p class="note">次に書くべき資料か、既存の資料に足すべき節の候補です。
    名前を押すと、下の一覧のその行へ飛びます。</p>
  __TODO__

  <h2><em>COVERAGE</em>テーマ別の網羅性</h2>
  <p class="note">1行が1つの概念です。<b>帯の左端はそろえてあるので、
    上から下へ見ていけば多い少ないがそのまま比べられます</b>。
    薄い青が「触れている資料」、赤が「厚く扱う資料」。
    群の中は本数の少ない順なので、手薄なものが上に来ます。</p>
  __GROUPS__

  <h2><em>ORPHANS</em>孤立している資料</h2>
  <p class="note">どの概念にも触れていない資料です。
    本当に独立した話題ならそれでよく、そうでなければ拾う語が足りていません。</p>
  __ORPHAN__

  <h2><em>PAIRS</em>近い2本</h2>
  <p class="note">同じ概念を厚く扱っている組です。片方を直したら、もう片方も確かめます。</p>
  <ul class="edges">__EDGES__</ul>

  <details class="more">
    <summary>資料 × 概念の全格子をひらく
      <em>細かく突き合わせたいときだけ。__NDOC__ 行 × __NCON__ 列</em></summary>
    <div class="inner">
      <div class="bar">
        <input id="q" type="search" placeholder="資料をしぼり込む" autocomplete="off">
        <div class="legend">
          <span class="k4"><i>◎</i>正典</span>
          <span class="k3"><i>●</i>厚く扱う</span>
          <span class="k2"><i>●</i>触れる</span>
          <span class="k1"><i>・</i>言及あり</span>
        </div>
        <button class="rst" type="button">しぼり込みを解除</button>
      </div>
      <div class="scroll">
        <table class="mx">
          <thead>
            <tr><th class="r"></th>__HEAD1__<th></th></tr>
            <tr><th class="r">DOCUMENT</th>__HEAD2__<th></th></tr>
          </thead>
          <tbody>__BODY__</tbody>
        </table>
      </div>
    </div>
  </details>

  <footer>
    <span>OZAKEN / AICX ─ MATRIX</span>
    <span><a href="index.html">index</a> ／ <a href="backstage.html">裏資料置き場</a></span>
  </footer>
</div>
<script>
(function(){
  var q = document.getElementById('q');
  if (!q) return;
  var rows = Array.prototype.slice.call(document.querySelectorAll('tbody tr'));
  function run(){
    var v = q.value.trim().toLowerCase();
    rows.forEach(function(tr){
      if (tr.classList.contains('grp')) return;
      tr.classList.toggle('hide', !!v && tr.textContent.toLowerCase().indexOf(v) < 0);
    });
  }
  q.addEventListener('input', run);
  document.querySelector('button.rst').addEventListener('click', function(){
    q.value = ''; run(); q.focus();
  });
})();
</script>
</body>
</html>
"""
