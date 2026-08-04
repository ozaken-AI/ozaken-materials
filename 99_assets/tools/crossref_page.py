#!/usr/bin/env python3
"""資料マトリクスのページを組む。

crossref.py が集めた「どの資料が、どの概念に触れているか」を、
資料 × 概念 の格子として並べる。狙いは3つ。

  1. 資料が孤立していないかを見る（どこにも触れていない資料は、リンクの入り口が無い）
  2. 概念が散らばっていないかを見る（正典が決まっていない概念は、説明が食い違う）
  3. 資料どうしの近さを見る（同じ概念を厚く扱う2本は、主張を揃える必要がある）

ページ自体は資料ではないので、ozaken-web-style の規約（奇数セクション等）は適用しない。
パスワード台帳と同じ、道具としてのページ。
"""
import html as H
import os

from crossref_data import CONCEPTS, GROUPS

# セルの濃さ。言及回数で3段
HEAVY = 8


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


def build(rows, edges, stamp):
    """rows: [(rel, title, {概念名: 回数}), ...] / edges: [(a, b, w), ...]"""
    names = [n for _, ns in GROUPS for n in ns if n in CONCEPTS]
    # GROUPS に載せ忘れた概念があっても落とさない
    names += [n for n in CONCEPTS if n not in names]

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

    body, cur, alone, hot = [], None, [], {}
    for rel, title, hits in rows:
        d = os.path.dirname(rel) or 'そのほか'
        if d != cur:
            cur = d
            body.append('<tr class="grp"><th colspan="%d">%s</th></tr>'
                        % (len(names) + 2, H.escape(d)))
        cells, score, mine = [], 0, 0
        for n in names:
            canon = CONCEPTS[n][0]
            td, lv = _cell(rel, n, hits.get(n, 0), canon)
            cells.append(td)
            if lv == 4:
                mine += 1
            elif lv:
                score += 1
            if lv >= 3:
                hot[n] = hot.get(n, 0) + 1
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

    nofocus = [n for n in names if not hot.get(n)]
    thin = ('<ul class="thin">%s</ul>'
            % ''.join('<li>%s</li>' % H.escape(n) for n in nofocus)) if nofocus else \
           '<p class="none">すべての概念が、正典の外でも厚く扱われています。</p>'

    out = TEMPLATE
    for k, v in (('__HEAD1__', ''.join(head1)), ('__HEAD2__', ''.join(head2)),
                 ('__BODY__', '\n'.join(body)), ('__EDGES__', ''.join(ed)),
                 ('__ORPHAN__', orphan), ('__THIN__', thin),
                 ('__NDOC__', str(len(rows))), ('__NCON__', str(len(names))),
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
  --red:#e23744;--red-bright:#ff5d6a;--muted:#6b7a99;--amber:#c9762f;
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
.lead{font-size:.86rem;color:rgba(216,228,240,.75);margin-bottom:1.4rem;max-width:62ch}
.stats{display:flex;flex-wrap:wrap;gap:.7rem;margin-bottom:1.2rem}
.stat{flex:1;min-width:130px;padding:.8rem 1rem;border-radius:12px;
  background:rgba(255,255,255,.06);border:1px solid rgba(216,228,240,.16)}
.stat b{display:block;font-family:var(--fe);font-size:1.6rem;font-weight:700;line-height:1.2}
.stat span{font-size:.72rem;color:rgba(216,228,240,.7)}
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
th.c.on a{color:var(--red-bright);font-weight:700}
th.r,td.sum,.corner{position:sticky;left:0;background:#16233f;z-index:1}
th.r{min-width:230px;text-align:left;padding:.42rem .7rem;font-weight:400;
  border-right:1px solid rgba(216,228,240,.16)}
th.r a{text-decoration:none;color:#fff;display:block}
th.r .t{display:block;font-size:.78rem;line-height:1.35;overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}
th.r .p{display:block;font-family:var(--fe);font-size:.58rem;color:rgba(216,228,240,.42);
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
th.r a:hover .t{color:#9fc6f5}
.corner{top:0!important;z-index:4!important;background:#16233f!important;
  font-family:var(--fe);font-size:.6rem;letter-spacing:.14em;
  color:rgba(159,198,245,.7);text-align:left;padding:0 .7rem;
  border-right:1px solid rgba(216,228,240,.16)}
tr.grp th{position:sticky;left:0;text-align:left;font-family:var(--fe);font-size:.6rem;
  font-weight:700;letter-spacing:.14em;color:rgba(159,198,245,.8);
  background:#1b2c4d;padding:.3rem .7rem;border-top:1px solid rgba(216,228,240,.18)}
td.v{width:26px;min-width:26px;text-align:center;padding:.42rem 0;
  font-family:var(--fe);font-size:.8rem;line-height:1.35}
td.v4{color:var(--red-bright);text-shadow:0 0 10px rgba(255,93,106,.55)}
td.v3{color:#9fc6f5}
td.v2{color:rgba(159,198,245,.6);font-size:.6rem}
td.v1{color:rgba(216,228,240,.34);font-size:.7rem}
td.sum{width:52px;min-width:52px;text-align:right;padding:.42rem .7rem;font-family:var(--fe);
  font-size:.68rem;left:auto;right:0;border-left:1px solid rgba(216,228,240,.12)}
td.sum b{color:var(--red-bright)}td.sum i{font-style:normal;color:rgba(216,228,240,.5);margin-left:.35em}
tbody tr:hover th.r,tbody tr:hover td{background:rgba(46,84,150,.3)}
tbody tr:hover th.r{background:#1d3055}
td.hi,th.c.hi{background:rgba(46,84,150,.26)}
tr.off{display:none}

.panes{display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));margin-top:1.6rem}
.pane{padding:1.1rem 1.3rem;border-radius:14px;background:rgba(255,255,255,.05);
  border:1px solid rgba(216,228,240,.16)}
.pane h2{font-family:var(--fm);font-size:1rem;font-weight:600;margin-bottom:.3rem}
.pane p.k{font-size:.74rem;color:rgba(216,228,240,.6);margin-bottom:.8rem;line-height:1.7}
.pane ul{list-style:none;font-size:.78rem}
.pane a{color:#cfe0f5;text-decoration:none}
.pane a:hover{color:#fff;text-decoration:underline}
.edges li{display:flex;align-items:baseline;gap:.5rem;padding:.28rem 0;
  border-bottom:1px solid rgba(216,228,240,.08)}
.edges .w{font-family:var(--fe);font-size:.66rem;color:var(--red-bright);
  min-width:2.2em;text-align:right}
.edges .x{color:rgba(216,228,240,.4)}
.edges a{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:42%}
.orphan li,.thin li{padding:.2rem 0;color:rgba(216,228,240,.8)}
.none{font-size:.78rem;color:#7ee2b0}
.note{margin-top:1.6rem;padding-top:1.2rem;border-top:1px solid rgba(216,228,240,.14);
  font-size:.74rem;line-height:1.9;color:rgba(216,228,240,.55)}
.note code{font-family:var(--fe);background:rgba(255,255,255,.08);padding:.1em .45em;
  border-radius:4px;color:#fff}
.note a{color:var(--azure-pale)}
@media(max-width:720px){th.r{min-width:150px;max-width:150px}}
</style>
</head>
<body>
<div class="wrap">
  <div class="badge"><span class="dot"></span><span class="ja">おざけん コンテンツ管理システム</span></div>
  <h1>資料マトリクス</h1>
  <p class="lead">どの資料が、どの概念に触れているか。◎の資料がその概念の正典で、
  ほかの資料は末尾の「関連する資料」からそこへつながっています。
  同じ概念を厚く扱う資料どうしは、主張が食い違っていないかを確かめる対象です。最終更新 __STAMP__</p>

  <div class="stats">
    <div class="stat"><b>__NDOC__</b><span>資料</span></div>
    <div class="stat"><b>__NCON__</b><span>概念</span></div>
    <div class="stat"><b>__NEDGE__</b><span>資料どうしのつながり</span></div>
  </div>

  <div class="bar">
    <input id="q" type="search" placeholder="資料をしぼり込む" autocomplete="off">
    <div class="legend">
      <span><i class="k4">◎</i>正典</span>
      <span><i class="k3">●</i>厚く扱う</span>
      <span><i class="k2">●</i>触れる</span>
      <span><i class="k1">・</i>言及あり</span>
    </div>
    <button class="rst" id="rst" type="button">しぼり込みを解除</button>
  </div>

  <div class="scroll">
    <table class="mx">
      <thead>
        <tr><th class="corner" rowspan="2">DOCUMENT</th>__HEAD1__<th rowspan="2"></th></tr>
        <tr>__HEAD2__</tr>
      </thead>
      <tbody id="tb">
__BODY__
      </tbody>
    </table>
  </div>

  <div class="panes">
    <div class="pane">
      <h2>つながりの強い組み合わせ</h2>
      <p class="k">同じ概念を厚く扱っている2本。数字が大きいほど重なりが大きく、
      説明が食い違っていると目立ちます。</p>
      <ul class="edges">__EDGES__</ul>
    </div>
    <div class="pane">
      <h2>どこにもつながっていない資料</h2>
      <p class="k">既知の概念にひとつも触れていない資料。独立した話題なら問題ありませんが、
      本来つながるはずなら <code>crossref_data.py</code> に拾う語が足りていません。</p>
      __ORPHAN__
    </div>
    <div class="pane">
      <h2>正典の外で厚く扱われていない概念</h2>
      <p class="k">ほかの資料が軽くしか触れていない概念。
      講演で繰り返し語るものなら、各資料に一段深い説明を足す余地があります。</p>
      __THIN__
    </div>
  </div>

  <p class="note">
    このページは <code>99_assets/tools/crossref.py matrix</code> が生成します。手で書き換えないでください。<br>
    概念と正典の対応は <code>99_assets/tools/crossref_data.py</code>。資料を足したらここに登録します。<br>
    <a href="index.html">← AI資料アーカイブに戻る</a>
  </p>
</div>
<script>
/* 列を選ぶと、その概念に触れている資料だけが残る。
   投影しながら「この話は、この資料とこの資料でしています」と示すため */
(function(){
  var tb=document.getElementById('tb'), q=document.getElementById('q'),
      rst=document.getElementById('rst'),
      heads=[].slice.call(document.querySelectorAll('th.c'));
  var col=-1, text='';

  function apply(){
    [].forEach.call(tb.rows, function(tr){
      if(tr.classList.contains('grp')) return;
      var ok=true;
      if(col>=0){ var td=tr.cells[col+1]; ok = td && !td.classList.contains('v0'); }
      if(ok && text){ ok = tr.cells[0].textContent.toLowerCase().indexOf(text)>=0; }
      tr.classList.toggle('off', !ok);
    });
    /* 見出しだけが残った区分は隠す */
    var last=null, seen=false;
    [].forEach.call(tb.rows, function(tr){
      if(tr.classList.contains('grp')){
        if(last) last.classList.toggle('off', !seen);
        last=tr; seen=false;
      } else if(!tr.classList.contains('off')) seen=true;
    });
    if(last) last.classList.toggle('off', !seen);
  }
  heads.forEach(function(th,i){
    th.addEventListener('click', function(e){
      e.preventDefault();
      col = (col===i) ? -1 : i;
      heads.forEach(function(h,j){ h.classList.toggle('on', j===col); });
      apply();
    });
  });
  q.addEventListener('input', function(){ text=q.value.trim().toLowerCase(); apply(); });
  rst.addEventListener('click', function(){
    col=-1; text=''; q.value='';
    heads.forEach(function(h){ h.classList.remove('on'); });
    apply();
  });

  /* 縦の筋を見せる。行の hover は CSS が持っているので、ここは列だけ */
  var hi=-1;
  tb.addEventListener('mouseover', function(e){
    var td=e.target.closest ? e.target.closest('td.v') : null;
    if(!td) return;
    var i=td.cellIndex;
    if(i===hi) return;
    hi=i;
    [].forEach.call(tb.rows, function(tr){
      [].forEach.call(tr.cells, function(c,j){ c.classList.toggle('hi', j===i); });
    });
    heads.forEach(function(h,j){ h.classList.toggle('hi', j===i-1); });
  });
})();
</script>
</body>
</html>
"""
