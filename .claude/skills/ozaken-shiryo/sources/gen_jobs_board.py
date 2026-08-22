#!/usr/bin/env python3
"""日米 雇用統計ダッシュボード（12_jobs/us-jp-employment.html）

**これは投影用の解説資料ではない。板（ボード）である。**

最初は9面18図の資料として組んだが、読み物になっていた。
ダッシュボードに求められるのは、**開いた瞬間に現在地が分かること**。
導入文もカードも要らない。数字と、それが何の数字かと、いつの分か。
それだけを、上から重要な順に置く。

だから資料の型（build_page）には通していない。
面の明暗の交互も、9面18図も、この板には関係がない。

  python3 gen_jobs_board.py                              # HTMLを書き出す
  OZAKEN_PW=マスター python3 ../scripts/put_board.py     # 鍵を保ったまま差し替える

**数字を差し替えるときは、DATA のところだけ直す。** 見た目には触らない。
"""
import datetime
import html
import os

OUT = '/tmp/board_jobs.html'
STAMP = '2026年8月22日'

# ══════════════════════════════════════════════════════════════
# ここから下が中身。**新しい発表が出たら、ここだけ直す。**
# ══════════════════════════════════════════════════════════════

LEAD = ('日本は<b>人が足りないから</b>低く、'
        '米国は<b>探すのをやめた人が増えたから</b>低い。'
        '失業率は「いま仕事を探している人」しか数えないので、'
        'まったく逆の状態が、同じ数字として出てきます。')

# (数値, 単位, 何の数字か, いつの分, ひとこと, 色 azure|red|plain)
JP_KPI = [
    ('2.5', '%', '完全失業率', '2026年6月', '4月・5月・6月と同じ水準', 'azure'),
    ('1.18', '倍', '有効求人倍率', '2026年6月', '1人に1.18件。前月から+0.01', 'azure'),
    ('6,880', '万人', '就業者数', '2026年4〜6月期', '前年同期から+44万人', 'azure'),
    ('+3.4', '%', '現金給与総額（前年同月比）', '2026年6月', '5か月続けて3%以上', 'azure'),
]
US_KPI = [
    ('4.1', '%', '失業率', '2026年7月', '前月から低下。ただし下は見てください', 'azure'),
    ('-2.3', '万人', '雇用者数の増減（非農業）', '2026年7月', '6月も-2.0万人。2か月続けて減少', 'red'),
    ('61.4', '%', '労働参加率', '2026年7月', '5年を超えて最も低い', 'red'),
    ('+3.4', '万人', '雇用の増加ペース（12か月平均）', '2026年7月まで', '月あたり。1年前より大きく低下', 'plain'),
]

JP_ROWS = [
    ('新規求人倍率', '2.16倍', '2026年6月', '前月から+0.05ポイント'),
    ('正規の職員・従業員', '3,741万人', '2026年6月', '前年同月から+21万人。32か月続けて増加'),
    ('非正規の職員・従業員', '2,157万人', '2026年6月', '前年同月から+20万人。3か月続けて増加'),
    ('実質賃金（前年同月比）', '+1.9%', '2026年4月', '4か月続けてプラス'),
    ('現金給与総額', '31.2万円', '2026年4月', '前年同月比+3.5%。6月は賞与が入るため比べない'),
]
US_ROWS = [
    ('雇用者数の増減', '+6.3万人', '2026年5月', '当初の発表から6.6万人ぶん下方修正された'),
    ('雇用者数の増減', '-2.0万人', '2026年6月', 'ここで、増加から減少へ変わった'),
    ('雇用者数の増減', '-2.3万人', '2026年7月', '市場予想は+8.3万人だった'),
    ('就業者比率', '58.9%', '2026年7月', '働いている人が、人口に占める割合'),
]

# 入口（新卒・若手）。日米を横に並べる
ENTRY = [
    ('米国', '22〜27歳・大卒の失業率', '5.6%', '2026年Q2', '全体の4.1%より高い', 'red'),
    ('米国', '同年代の不完全雇用率', '42%', '2026年Q2', '大卒を必要としない仕事に就いている割合', 'red'),
    ('米国', '22〜65歳・大卒の失業率', '3.1%', '2026年Q2', '同じ大卒でも、年齢が上がるとこの水準', 'plain'),
    ('日本', '大卒求人倍率（2027年卒）', '1.62倍', '2026年4月', '前年（2026年卒）は1.66倍', 'amber'),
    ('日本', '民間企業の求人総数', '74.8万人', '2026年4月', '前年の76.5万人から1.7万人の減少', 'amber'),
    ('日本', '大卒の平均初任給（月額）', '23.7万円', '2026年4月入社', '4年続けて増加', 'plain'),
]

# 2040年の推計（経済産業省）
SHORT = [('AI・ロボット等利活用人材', '約340万人'),
         ('現場人材', '約260万人'),
         ('理系人材', '約120万人')]
SURPLUS = [('事務職', '約440万人'),
           ('文系人材', '約80万人')]

# 見る順番
WATCH = [
    ('有効求人倍率', '厚生労働省', '翌月末ごろ', '採りたい企業の意欲が、いちばん早く出る'),
    ('労働参加率', '米労働統計局', '翌月 第1金曜', '失業率が下がった理由が、ここで分かる'),
    ('雇用者数（非農業）', '米労働統計局', '翌月 第1金曜', '失業率と逆を向くことがある。12か月平均で見る'),
    ('完全失業率・就業者数', '総務省', '翌月末ごろ', '総量の確認。大きくは動かない'),
    ('現金給与総額・実質賃金', '厚生労働省', '翌々月上旬', '人手不足が本物かどうかが、単価に出る'),
    ('大卒求人倍率', 'リクルートワークス研究所', '毎年4月ごろ', '入口の広さ。年1回だが、方向がよく分かる'),
]

SOURCES = [
    '総務省「労働力調査（基本集計）」2026年6月分',
    '厚生労働省「一般職業紹介状況」2026年6月分（7月31日発表）',
    '厚生労働省「毎月勤労統計調査」2026年3月分・4月分・6月分の速報',
    '米労働統計局「Employment Situation」2026年7月分（8月7日発表）',
    'ニューヨーク連邦準備銀行「The Labor Market for Recent College Graduates」2026年第2四半期まで',
    'リクルートワークス研究所「第43回 ワークス大卒求人倍率調査（2027年卒）」',
    '経済産業省「2040年の就業構造推計（改訂版）」2026年3月',
]

# ══════════════════════════════════════════════════════════════
# ここから下は見た目。中身を直すときは触らない
# ══════════════════════════════════════════════════════════════

E = html.escape


def kpi(rows):
    out = []
    for v, u, what, when, note, tone in rows:
        out.append(
            '<div class="kpi t-%s">'
            '<p class="k-what">%s</p>'
            '<p class="k-v">%s<span>%s</span></p>'
            '<p class="k-when">%s</p>'
            '<p class="k-note">%s</p>'
            '</div>' % (tone, E(what), E(v), E(u), E(when), E(note)))
    return '\n'.join(out)


def table(head, rows):
    th = ''.join('<div class="th">%s</div>' % E(h) for h in head)
    tr = ''
    for r in rows:
        tr += '<div class="tr">' + ''.join(
            '<div class="td">%s</div>' % E(c) for c in r) + '</div>'
    return ('<div class="tbl" style="--cols:%d"><div class="tr th-row">%s</div>%s</div>'
            % (len(head), th, tr))


def entry_rows():
    out = ''
    for country, what, v, when, note, tone in ENTRY:
        out += ('<div class="er t-%s">'
                '<span class="er-c">%s</span>'
                '<span class="er-w">%s</span>'
                '<span class="er-v">%s</span>'
                '<span class="er-t">%s</span>'
                '<span class="er-n">%s</span>'
                '</div>' % (tone, E(country), E(what), E(v), E(when), E(note)))
    return out


PAGE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>日米 雇用統計ダッシュボード | おざけん</title>
<meta name="description" content="日本と米国の雇用統計を、同じ物差しで一枚に。失業率・求人倍率・雇用者数・労働参加率・賃金・新卒の入口・2040年の推計まで、出どころと確認日つき。新しい発表が出るたびに差し替えます。">
<meta name="theme-color" content="#131c33">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;600;700&family=Shippori+Mincho+B1:wght@500;600&family=Zen+Kaku+Gothic+New:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
:root{
  --navy:#1f3864;--navy-deep:#131c33;--azure:#2e5496;--azure-pale:#d8e4f0;
  --sky:#9fc6f5;--red:#e23744;--red-bright:#ff5d6a;--amber:#c9762f;
  --ink:#1a1a2e;--muted:#6b7a99;--white:#fff;--line:rgba(159,198,245,.16);
  --font-ja-sans:'Zen Kaku Gothic New',sans-serif;
  --font-ja-serif:'Shippori Mincho B1',serif;
  --font-en:'Hanken Grotesk',sans-serif;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{background:var(--navy-deep);-webkit-text-size-adjust:100%}
body{
  font-family:var(--font-ja-sans);color:var(--azure-pale);line-height:1.75;
  background:
    radial-gradient(120% 80% at 78% -8%,rgba(46,84,150,.55),transparent 62%),
    linear-gradient(168deg,#1f3864 0%,#182c55 42%,#131c33 100%);
  background-attachment:fixed;
  padding:clamp(1.2rem,3.2vw,2.4rem) clamp(1rem,3.2vw,2.4rem) 4rem;
}
.wrap{max-width:1360px;margin:0 auto}

/* ── 見出し帯 ───────────────────────────── */
.top{display:flex;flex-wrap:wrap;align-items:flex-end;gap:1rem 1.6rem;
  padding-bottom:1.1rem;border-bottom:1px solid var(--line);margin-bottom:1.5rem}
.badge{display:inline-flex;align-items:center;gap:.55em;
  font-family:var(--font-en);font-size:.6rem;font-weight:700;letter-spacing:.26em;
  color:var(--sky);border:1px solid var(--line);border-radius:100px;
  padding:.34em .95em;margin-bottom:.75rem}
.badge i{width:5px;height:5px;border-radius:50%;background:#46c98a;
  animation:blink 2.4s ease-in-out infinite;font-style:normal}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
h1{font-family:var(--font-ja-sans);font-weight:800;color:#fff;
  font-size:clamp(1.35rem,3.1vw,2.05rem);line-height:1.3;letter-spacing:.01em}
.h-sub{font-family:var(--font-ja-serif);font-size:clamp(.86rem,1.5vw,1rem);
  color:var(--sky);margin-top:.4rem}
.stamp{margin-left:auto;text-align:right;font-family:var(--font-en);
  font-size:.66rem;letter-spacing:.14em;color:rgba(216,228,240,.5);line-height:2}
.stamp b{display:block;font-size:.9rem;color:#fff;letter-spacing:.06em}

/* ── 読み ───────────────────────────────── */
.lead{font-family:var(--font-ja-serif);font-size:clamp(.95rem,1.9vw,1.2rem);
  line-height:1.95;color:rgba(255,255,255,.93);
  border-left:3px solid var(--azure);padding:.1rem 0 .1rem 1.1rem;
  margin-bottom:1.9rem;max-width:74ch}
.lead b{color:var(--red-bright);font-weight:700}

/* ── 国の板 ─────────────────────────────── */
.pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1.1rem;
  margin-bottom:1.1rem}
.panel{background:rgba(159,198,245,.055);border:1px solid var(--line);
  border-radius:14px;padding:1.15rem 1.15rem 1.3rem}
.p-head{display:flex;align-items:baseline;gap:.7em;margin-bottom:.95rem}
.p-head h2{font-size:1.05rem;font-weight:800;color:#fff}
.p-head span{font-family:var(--font-en);font-size:.6rem;font-weight:700;
  letter-spacing:.2em;color:rgba(159,198,245,.6)}
.kpis{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.65rem}
.kpi{background:rgba(19,28,51,.4);border:1px solid var(--line);
  border-radius:10px;padding:.8rem .85rem .85rem;position:relative;overflow:hidden}
.kpi::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;
  background:var(--azure)}
.kpi.t-red::before{background:var(--red-bright)}
.kpi.t-amber::before{background:var(--amber)}
.kpi.t-plain::before{background:rgba(159,198,245,.35)}
.k-what{font-size:.72rem;font-weight:700;color:rgba(255,255,255,.9);
  line-height:1.5;min-height:2.2em}
.k-v{font-family:var(--font-en);font-size:clamp(1.6rem,3.4vw,2.15rem);
  font-weight:700;line-height:1.15;letter-spacing:-.02em;color:#fff;margin:.25rem 0 .1rem}
.kpi.t-red .k-v{color:var(--red-bright)}
.k-v span{font-family:var(--font-ja-sans);font-size:.62rem;font-weight:700;
  margin-left:.3em;color:rgba(216,228,240,.72);letter-spacing:0}
.k-when{font-family:var(--font-en);font-size:.6rem;letter-spacing:.08em;
  color:rgba(159,198,245,.65)}
.k-note{font-size:.66rem;line-height:1.65;color:rgba(216,228,240,.6);margin-top:.3rem}

/* ── 表 ─────────────────────────────────── */
.block{background:rgba(159,198,245,.05);border:1px solid var(--line);
  border-radius:14px;padding:1.15rem 1.15rem 1.25rem;margin-bottom:1.1rem}
.b-head{display:flex;align-items:baseline;gap:.7em;margin-bottom:.9rem}
.b-head h2{font-size:.95rem;font-weight:800;color:#fff}
.b-head span{font-family:var(--font-en);font-size:.58rem;font-weight:700;
  letter-spacing:.2em;color:rgba(159,198,245,.55)}
.tbl{display:flex;flex-direction:column;font-size:.74rem}
.tr{display:grid;grid-template-columns:repeat(var(--cols),minmax(0,1fr));
  gap:.6rem;padding:.5rem .2rem;border-bottom:1px solid rgba(159,198,245,.1)}
.tr:last-child{border-bottom:0}
.th-row{border-bottom:1px solid rgba(159,198,245,.28)}
.th{font-family:var(--font-en);font-size:.58rem;font-weight:700;letter-spacing:.14em;
  color:rgba(159,198,245,.6)}
.td{color:rgba(216,228,240,.82);line-height:1.6;min-width:0;overflow-wrap:anywhere}
.tr .td:first-child{font-weight:700;color:#fff}
.tr .td:nth-child(2){font-family:var(--font-en);color:var(--sky);font-weight:600}

/* ── 入口 ───────────────────────────────── */
.entry{display:grid;gap:.5rem}
.er{display:grid;grid-template-columns:3.4rem minmax(0,1.5fr) 5.2rem 5.6rem minmax(0,2fr);
  gap:.7rem;align-items:baseline;font-size:.74rem;
  padding:.62rem .8rem;border-radius:9px;background:rgba(19,28,51,.36);
  border-left:3px solid rgba(159,198,245,.35)}
.er.t-red{border-left-color:var(--red-bright)}
.er.t-amber{border-left-color:var(--amber)}
.er-c{font-family:var(--font-en);font-size:.58rem;font-weight:700;letter-spacing:.14em;
  color:rgba(159,198,245,.65)}
.er-w{font-weight:700;color:#fff;line-height:1.5}
.er-v{font-family:var(--font-en);font-size:1rem;font-weight:700;color:var(--sky)}
.er.t-red .er-v{color:var(--red-bright)}
.er-t{font-family:var(--font-en);font-size:.6rem;letter-spacing:.06em;
  color:rgba(159,198,245,.6)}
.er-n{color:rgba(216,228,240,.62);line-height:1.6}

/* ── 2040年 ─────────────────────────────── */
.gap2040{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1.1rem}
.side h3{font-family:var(--font-en);font-size:.6rem;font-weight:700;letter-spacing:.2em;
  margin-bottom:.6rem}
.side.short h3{color:var(--sky)}
.side.surplus h3{color:var(--red-bright)}
.side ul{list-style:none}
.side li{display:flex;justify-content:space-between;gap:1rem;align-items:baseline;
  padding:.55rem .8rem;margin-bottom:.4rem;border-radius:8px;
  background:rgba(19,28,51,.36);border-left:3px solid var(--azure);font-size:.78rem}
.side.surplus li{border-left-color:var(--red-bright)}
.side li b{font-family:var(--font-en);font-weight:700;color:#fff;white-space:nowrap}
.g-note{grid-column:1/-1;font-size:.68rem;line-height:1.8;
  color:rgba(216,228,240,.55);margin-top:.2rem}

/* ── 出典 ───────────────────────────────── */
.src{font-size:.68rem;line-height:1.95;color:rgba(216,228,240,.55)}
.src li{list-style:none;padding-left:1.1em;position:relative}
.src li::before{content:"";position:absolute;left:0;top:.75em;width:5px;height:1px;
  background:rgba(159,198,245,.5)}
.warn{margin-top:.9rem;padding:.75rem .9rem;border-radius:9px;
  background:rgba(226,55,68,.09);border:1px solid rgba(255,93,106,.3);
  font-size:.7rem;line-height:1.8;color:rgba(255,255,255,.85)}
.warn b{color:var(--red-bright)}
.foot{margin-top:1.6rem;padding-top:1.1rem;border-top:1px solid var(--line);
  display:flex;flex-wrap:wrap;gap:.6rem 1.4rem;align-items:center;
  font-size:.7rem;color:rgba(216,228,240,.5)}
.foot a{color:var(--sky);text-decoration:none}
.foot a:hover{text-decoration:underline}

@media(max-width:900px){
  .pair,.gap2040{grid-template-columns:1fr}
  .er{grid-template-columns:3.2rem minmax(0,1fr) 4.6rem;row-gap:.2rem}
  .er-t,.er-n{grid-column:2/-1;font-size:.66rem}
}
@media(max-width:560px){
  .kpis{grid-template-columns:1fr}
  .tr{grid-template-columns:1fr;gap:.1rem;padding:.6rem .2rem}
  .th-row{display:none}
  .tr .td:first-child{font-size:.8rem}
}
@media print{
  body{background:#fff;color:#1a1a2e}
  .panel,.block,.kpi,.er,.side li{background:#fff;border-color:#d8e4f0}
}
</style>
</head>
<body>
<div class="wrap">

  <header class="top">
    <div>
      <span class="badge"><i></i>OZAKEN CMS ／ EMPLOYMENT BOARD</span>
      <h1>日米 雇用統計ダッシュボード</h1>
      <p class="h-sub">同じ「低い失業率」が、正反対の意味を持つ</p>
    </div>
    <div class="stamp">UPDATED<b>__STAMP__</b>新しい発表が出るたびに差し替えます</div>
  </header>

  <p class="lead">__LEAD__</p>

  <div class="pair">
    <section class="panel">
      <div class="p-head"><h2>日本</h2><span>JAPAN</span></div>
      <div class="kpis">__JP_KPI__</div>
    </section>
    <section class="panel">
      <div class="p-head"><h2>米国</h2><span>UNITED STATES</span></div>
      <div class="kpis">__US_KPI__</div>
    </section>
  </div>

  <div class="pair">
    <section class="block">
      <div class="b-head"><h2>日本 ─ そのほかの数字</h2><span>DETAIL</span></div>
      __JP_TBL__
    </section>
    <section class="block">
      <div class="b-head"><h2>米国 ─ 月ごとの雇用者数</h2><span>MONTHLY</span></div>
      __US_TBL__
    </section>
  </div>

  <section class="block">
    <div class="b-head"><h2>入口 ─ 新卒と若手</h2><span>ENTRY LEVEL</span></div>
    <div class="entry">__ENTRY__</div>
  </section>

  <section class="block">
    <div class="b-head"><h2>2040年の推計 ─ 日本</h2><span>OUTLOOK 2040</span></div>
    <div class="gap2040">
      <div class="side short"><h3>足りなくなる</h3><ul>__SHORT__</ul></div>
      <div class="side surplus"><h3>余ってしまう</h3><ul>__SURPLUS__</ul></div>
      <p class="g-note">左右の行は対応していません。余った人がそのまま足りない場所へ移る、
        という推計ではなく、不足と余剰が別の場所で同時に起きるという推計です。
        就業者数は約6,700万人（2022年）から約6,300万人へ減ると見込まれています。</p>
    </div>
  </section>

  <section class="block">
    <div class="b-head"><h2>見る順番と、発表の時期</h2><span>WHAT TO WATCH</span></div>
    __WATCH__
  </section>

  <section class="block">
    <div class="b-head"><h2>出典</h2><span>SOURCES</span></div>
    <ul class="src">__SOURCES__</ul>
    <p class="warn"><b>この板の数字は、二次情報を含みます。</b>
      統計機関のサイトへ直接到達できない環境で作っているため、
      各機関の発表を伝える報道にもとづく数字が含まれます。
      重要な判断に使う前は、各機関の原典で確かめてください。確認日 __STAMP__。</p>
  </section>

  <footer class="foot">
    <span>小澤健祐（おざけん）／ 一般社団法人AICX協会 代表理事</span>
    <a href="../index.html">← AI資料アーカイブ</a>
  </footer>

</div>
</body>
</html>
"""


def build():
    page = PAGE
    for k, v in (
        ('__STAMP__', STAMP),
        ('__LEAD__', LEAD),
        ('__JP_KPI__', kpi(JP_KPI)),
        ('__US_KPI__', kpi(US_KPI)),
        ('__JP_TBL__', table(['何の数字か', '直近の値', 'いつの分', '動き'], JP_ROWS)),
        ('__US_TBL__', table(['何の数字か', '値', 'いつの分', '注記'], US_ROWS)),
        ('__ENTRY__', entry_rows()),
        ('__SHORT__', ''.join('<li>%s<b>%s</b></li>' % (E(a), E(b)) for a, b in SHORT)),
        ('__SURPLUS__', ''.join('<li>%s<b>%s</b></li>' % (E(a), E(b)) for a, b in SURPLUS)),
        ('__WATCH__', table(['何を見るか', 'どこが出すか', 'いつ出るか', 'なぜ先に見るか'], WATCH)),
        ('__SOURCES__', ''.join('<li>%s</li>' % E(x) for x in SOURCES)),
    ):
        page = page.replace(k, v)
    return page


if __name__ == '__main__':
    open(OUT, 'w', encoding='utf-8').write(build())
    print('板を書き出しました: %s（%d 文字）' % (OUT, len(build())))
